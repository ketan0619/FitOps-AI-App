from flask import Flask, render_template, request, redirect, session, send_file
from models import db, User, Progress
from fitops import calculate_bmi, fitness_plan, ideal_weight, calories_needed
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/fitops'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/generate', methods=['POST'])
def generate():
    age = int(request.form['age'])
    height = float(request.form['height'])
    weight = float(request.form['weight'])
    gender = request.form['gender']
    diet_type = request.form['diet_type']

    bmi = calculate_bmi(weight, height)
    ideal = ideal_weight(height)
    calories = calories_needed(weight, height, age, gender)
    plan = fitness_plan(bmi, age, gender, diet_type)

    result = {**plan, "bmi": bmi, "ideal": ideal, "calories": calories}
    session['report'] = result

    user = User.query.filter_by(username=session['user']).first()
    db.session.add(Progress(user_id=user.id, bmi=bmi, weight=weight))
    db.session.commit()

    return render_template('result.html', result=result)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()
        if user:
            session['user'] = user.username
            return redirect('/')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db.session.add(User(
            username=request.form['username'],
            password=request.form['password']
        ))
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/download')
def download():
    data = session.get('report')

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = [
        Paragraph("FitOps AI", styles['Title']),
        Paragraph("Build your Body like you Build your Code", styles['Normal']),
        Spacer(1,10)
    ]

    for k,v in data.items():
        if isinstance(v,list):
            v=", ".join(v)
        content.append(Paragraph(f"{k}: {v}", styles['Normal']))

    doc.build(content)
    return send_file("report.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
