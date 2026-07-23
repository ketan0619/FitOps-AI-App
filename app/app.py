#App Code
from flask import (Flask, render_template, request,
 redirect, session, send_file, jsonify)
from flask_session import Session
from models import db, User, Progress
from fitops import calculate_bmi, fitness_plan, ideal_weight, calories_needed
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from io import BytesIO
import os
import time
import requests
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)

# ---------- DATABASE URI RESOLUTION FUNCTION (MOVED UP) ----------
_db_uri = None

def get_db_uri():
    """
    Resolve the DB connection string purely from environment variables.
    No AWS / Secrets Manager calls here — this app's DB is not on AWS,
    and the credentials are already injected as env vars via
    GitHub Actions / Kubernetes secrets.
    """
    global _db_uri
    if _db_uri:
        return _db_uri
    # Preferred: a single fully-formed DATABASE_URL env var
    full_url = os.getenv("DATABASE_URL")
    if full_url:
        _db_uri = full_url
        return _db_uri
    # Fallback: build it from individual pieces
    db_user = os.getenv("MYSQL_USER", "fitops")
    db_pass = os.getenv("MYSQL_PASSWORD", "fitops123")
    db_host = os.getenv("MYSQL_HOST", "mysql")
    db_port = os.getenv("MYSQL_PORT", "3306")
    db_name = os.getenv("MYSQL_DATABASE", "fitopsdb")
    _db_uri = (
        f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    return _db_uri

# ---------- FLASK CONFIGURATIONS ----------
# FIX #1: Register the Secret Key inside the config dictionary explicitly
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "fitops-secret")

# FIX #2: Configure Centralized Database-Backed Sessions for Multi-Replica EKS Pods
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_PERMANENT'] = False

# Resolve the DB connection string purely from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#fix
# Initialize extensions in order
db.init_app(app)
Session(app) # Initializes the central state manager cleanly

# ---------- LOGIN REQUIRED DECORATOR ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# ---------- DATABASE INITIALIZATION & RETRY LOOP ----------
# Added retry logic to wait for MySQL to finish booting up
with app.app_context():
    for i in range(10): # Try 10 times
        try:
            db.create_all()
            print("Database connected and tables created successfully!")
            break
        except Exception as e:
            print(
                f"Database not ready yet (attempt {i+1}/10), "
                f"waiting... Error: {e}"
            )
            time.sleep(3) # Wait 3 seconds before retrying
    else:
        print("Could not connect to the database after 10 attempts.")

# ---------- MAIN / DASHBOARD ----------
@app.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        return redirect('/logout')
        
    # 1. Look for user's database footprint to build persistent baseline parameters
    latest_progress = Progress.query.filter_by(user_id=user.id).order_by(Progress.id.desc()).first()
    
    initial_inputs = {
        'age': str(latest_progress.user.age) if (latest_progress and hasattr(latest_progress.user, 'age')) else '',
        'height': str(int(session.get('last_height', 175))),
        'weight': str(latest_progress.weight) if latest_progress else '',
        'gender': 'male',
        'diet_type': 'normal'
    }
    
    # Pull existing layout variables out of the active user session if they exist
    if 'last_input' in session:
        initial_inputs.update(session['last_input'])
        
    # 2. Form Submission Action Execution Window
    if request.method == 'POST':
        try:
            weight = float(request.form.get('weight', 0))
            height = float(request.form.get('height', 0))
            age = int(request.form.get('age', 0))
            gender = request.form.get('gender', 'male')
            activity = request.form.get('activity', 'moderate')
            diet_type = request.form.get('diet_type', 'normal')
            
            # Cache current metrics into the session to persist them inside form fields
            session['last_height'] = height
            session['last_input'] = {
                'age': str(age),
                'height': str(int(height)),
                'weight': str(weight),
                'gender': gender,
                'diet_type': diet_type
            }
            
            # Run Matrix Math Algorithms
            bmi = calculate_bmi(weight, height)
            plan = fitness_plan(bmi, age, gender, diet_type)
            calories = calories_needed(weight, height, age, gender, activity)
            
            # Determine explicit visual index categories
            if bmi < 18.5: category = "Underweight"
            elif bmi < 25: category = "Normal"
            elif bmi < 30: category = "Overweight"
            else: category = "Obese"
            
            result = {
                **plan,
                "bmi": round(bmi, 1),
                "calories": calories,
                "ideal": ideal_weight(height),
                "category": category
            }
            session['report'] = result
            
            # Log historical timeline metrics into database
            progress = Progress(user_id=user.id, bmi=bmi, weight=weight, calories=calories)
            db.session.add(progress)
            db.session.commit()
            
            # Redirect straight to the results engine view page
            return render_template('result.html', result=result)
            
        except Exception as e:
            return f"Error executing biometric matrix: {str(e)}", 400
            
    # 3. GET Fallback Render Mode (Returns values to Home Dashboard)
    fallback_result = session.get('report', None)
    if not fallback_result and latest_progress:
        if latest_progress.bmi < 18.5: cat = "Underweight"
        elif latest_progress.bmi < 25: cat = "Normal"
        elif latest_progress.bmi < 30: cat = "Overweight"
        else: cat = "Obese"
        
        fallback_result = {
            "bmi": round(latest_progress.bmi, 1),
            "calories": latest_progress.calories,
            "category": cat
        }
        
    return render_template('dashboard.html', result=fallback_result, inputs=initial_inputs)

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username']
        ).first()
        if user and check_password_hash(
            user.password, request.form['password']
        ):
            session['user'] = user.username
            return redirect('/')
        return "Invalid username or password"
    return render_template('login.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing = User.query.filter_by(
            username=request.form['username']
        ).first()
        if existing:
            return "Username already exists"
        user = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# ---------- CHATBOT ----------
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    msg = request.json.get("message", "").strip()
    if not msg:
        return jsonify({"reply": "Input clear communication protocol parameters."})

    ollama_base = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    
    # Extract structural metrics content from user session
    report = session.get('report', None)
    biometric_context = "No metrics calculated yet."
    
    if report:
        biometric_context = (
            f"User's BMI: {report.get('bmi', 'N/A')} ({report.get('category', 'N/A')})\n"
            f"User's Daily Calorie Target: {report.get('calories', 'N/A')} KCAL\n"
            f"User's Primary Goal: {report.get('goal', 'N/A')}\n"
            f"User's Ideal Weight Range: {report.get('ideal', 'N/A')}"
        )

    # Tight, unbreachable ruleset specifically tuned for small parameter models
    system_rules = (
        "You are the FitOps AI Cyberpunk Fitness Expert Coach. Follow these instructions strictly:\n"
        "1. Answer the user's message directly, professionally, and enthusiastically.\n"
        "2. The provided data belongs to the USER, not you. Never say 'My BMI is...' or 'My goals are...'. Instead, say 'Your BMI is...'.\n"
        "3. Do NOT mention, repeat, or list the raw [USER BIOMETRICS MATRIX] strings unless specifically asked to summarize them.\n"
        "4. Do NOT output metadata like 'Sure, here's an answer:' or 'Assistant:'. Reply ONLY with your coach persona advice.\n\n"
        f"[USER BIOMETRICS MATRIX]:\n{biometric_context}"
    )

    try:
        # One-shot training sequence forces TinyLlama to copy the correct output style
        response = requests.post(
            f"{ollama_base}/api/chat",
            json={
                "model": "tinyllama",
                "messages": [
                    {"role": "system", "content": system_rules},
                    # One-Shot Example block teaches the model not to leak system tokens
                    {"role": "user", "content": "hello coach how are you"},
                    {"role": "assistant", "content": "Systems fully online and ready to push limits! I am here to help you optimize your recovery split and crush your training targets. Let me know what parameters we are tracking today!"},
                    {"role": "user", "content": msg}
                ],
                "stream": False,
                "options": {
                    "num_predict": 120,
                    "temperature": 0.1,  # Lowering temperature down to 0.1 maximizes logical rule compliance
                    "top_p": 0.9
                }
            },
            timeout=60
        )
        
        reply = response.json().get("message", {}).get("content", "").strip()
        
        # Post-generation filtering safeguards to catch fallback text leakage
        prefixes_to_clean = [
            "Sure, here's a possible answer for the user's message:",
            "Sure! Here is a possible answer:",
            "Coach Response:",
            "As an AI fitness coach,",
            "Assistant:"
        ]
        for prefix in prefixes_to_clean:
            if reply.startswith(prefix):
                reply = reply[len(prefix):].strip()
                
        if not reply:
            reply = "System matrix compiled cleanly. Let me know how to optimize your training parameters."

    except Exception as e:
        reply = f"Telemetry Error: Unable to sync with Coach AI engine cores. {str(e)}"
        
    return jsonify({"reply": reply})


# ---------- PROGRESS ----------
@app.route('/progress-data')
@login_required
def progress_data():
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    records = Progress.query.filter_by(user_id=user.id).all()
    return jsonify({
       "weights": [r.weight for r in records],
       "dates": [r.recorded_at.strftime('%Y-%m-%d') for r in records]
    })

# ---------- PDF ----------
@app.route('/download')
@login_required
def download():
    data = session.get('report')
    if not data:
        return "No report data available to download", 400

    from reportlab.lib.colors import HexColor
    from reportlab.platypus import Table, TableStyle, Image as RLImage

    buffer = BytesIO()

    # Page setup with 0.5 inch minimal margins
    doc = SimpleDocTemplate(
        buffer,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    # Cyberpunk Theme Colors
    bg_dark     = HexColor('#0d1017')
    panel_bg    = HexColor('#161a23')
    accent_red  = HexColor('#ff0055')
    accent_green = HexColor('#00ff66')
    text_white  = HexColor('#ffffff')
    text_gray   = HexColor('#94a3b8')

    styles = getSampleStyleSheet()

    # Custom Type Definitions
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=26, textColor=text_white,
        spaceAfter=4, alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, textColor=accent_green,
        spaceAfter=15, spaceBefore=0, leading=14
    )
    section_heading = ParagraphStyle(
        'SecHeading', parent=styles['Heading3'],
        fontName='Helvetica-Bold', fontSize=12, textColor=accent_red,
        spaceBefore=14, spaceAfter=8
    )
    body_white = ParagraphStyle(
        'BodyW', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, textColor=text_white, leading=14
    )
    body_gray = ParagraphStyle(
        'BodyG', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, textColor=text_gray, leading=14
    )

    content = []

    # --- 1. Header Banner ---
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png')
    header_content_left = []

    if os.path.exists(logo_path):
        try:
            logo_img = RLImage(logo_path, width=45, height=45)
            header_content_left.append(logo_img)
        except Exception:
            pass

    header_content_left.append([
        Paragraph("FITOPS AI RECOVERY MATRIX", title_style),
        Paragraph("PUMP IRON • TRACK DATA • OPTIMIZE RECOVERY", subtitle_style)
    ])

    # FIX #1: ternary now has a valid else value — [380] when no logo
    left_text_table = Table(
        [header_content_left],
        colWidths=[55, 325] if len(header_content_left) > 1 else [380]
    )
    left_text_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
    ]))

    header_data = [[
        left_text_table,
        Paragraph(
            "[ COACH ONLINE ]",
            ParagraphStyle(
                'Badge', parent=body_white,
                textColor=accent_green,
                fontName='Helvetica-Bold',
                alignment=2
            )
        )
    ]]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
    ]))
    content.append(header_table)

    # Decorative HR line
    line_table = Table([[""]], colWidths=[540], rowHeights=[2])
    line_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (0, 0), accent_green),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
    ]))
    content.append(line_table)
    content.append(Spacer(1, 15))

    # --- 2. Biometric Stats Grid ---
    stat_lbl_p   = ParagraphStyle('StatL', fontName='Helvetica-Bold', fontSize=8,  textColor=text_gray,   alignment=1)
    stat_val_p   = ParagraphStyle('StatV', fontName='Helvetica-Bold', fontSize=16, textColor=accent_green, alignment=1)
    stat_val_red = ParagraphStyle('StatVR', fontName='Helvetica-Bold', fontSize=14, textColor=accent_red,  alignment=1)

    stat_data = [
        [
            Paragraph("BODY MASS INDEX",     stat_lbl_p),
            Paragraph("CALORIC TARGET",       stat_lbl_p),
            Paragraph("CLASSIFICATION",       stat_lbl_p),
        ],
        [
            Paragraph(str(data.get('bmi', 'N/A')),                      stat_val_p),
            Paragraph(f"{data.get('calories', 'N/A')} KCAL",            stat_val_p),
            Paragraph(str(data.get('category', 'N/A')).upper(),         stat_val_red),
        ],
        [
            Paragraph("PRIMARY OBJECTIVE",    stat_lbl_p),
            Paragraph("IDEAL WEIGHT RANGE",   stat_lbl_p),
            "",
        ],
        [
            Paragraph(str(data.get('goal',  'N/A')).upper(),            stat_val_p),
            Paragraph(str(data.get('ideal', 'N/A')).upper(),            stat_val_p),
            "",
        ],
    ]

    stat_table = Table(stat_data, colWidths=[180, 180, 180])

    # FIX #2: merge base style + SPAN commands into ONE setStyle call
    # so the second call doesn't wipe the first
    stat_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), panel_bg),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR',     (0, 0), (-1, -1), text_white),
        ('INNERGRID',     (0, 0), (-1, -1), 1, HexColor('#1e2433')),
        ('BOX',           (0, 0), (-1, -1), 1, HexColor('#262e3d')),
        ('TOPPADDING',    (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        # SPAN commands now in the same call — not overwriting above styles
        ('SPAN',          (1, 2), (2, 2)),
        ('SPAN',          (1, 3), (2, 3)),
    ]))
    content.append(stat_table)

    # --- 3. Weekly Workout Plan ---
    content.append(Paragraph("WEEKLY WORKOUT PROTOCOL", section_heading))
    weekly_plan = data.get('weekly_plan', {})
    if isinstance(weekly_plan, dict):
        plan_rows = []
        for day, routine in weekly_plan.items():
            plan_rows.append([
                Paragraph(f"<b>{day.upper()}</b>", body_white),
                Paragraph(str(routine), body_gray)
            ])
        plan_table = Table(plan_rows, colWidths=[110, 430])
        plan_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), panel_bg),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('LEFTPADDING',   (0, 0), (-1, -1), 12),
            ('LINEBELOW',     (0, 0), (-1, -2), 0.5, HexColor('#1e2433')),
            ('BOX',           (0, 0), (-1, -1), 1, HexColor('#262e3d')),
        ]))
        content.append(plan_table)

    # --- 4. Coaching Tips ---
    content.append(Paragraph("STRATEGIC COACHING TIPS", section_heading))
    tips = data.get('tips', [])
    if isinstance(tips, list):
        for tip in tips:
            content.append(Paragraph(f"<font color='#00ff66'>&#9654;</font> {tip}", body_white))
            content.append(Spacer(1, 4))
    else:
        content.append(Paragraph(str(tips), body_white))

    # Background canvas
    def draw_background(canvas, document):
        canvas.saveState()
        canvas.setFillColor(bg_dark)
        canvas.rect(0, 0, document.pagesize[0], document.pagesize[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(content, onFirstPage=draw_background, onLaterPages=draw_background)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='fitops_matrix_report.pdf')


@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.after_request
def headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# ---------- LOGOUT PROTOCOL ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
