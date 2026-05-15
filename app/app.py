from flask import Flask, render_template, request, redirect, session, send_file, jsonify
from models import db, User, Progress
from fitops import calculate_bmi, fitness_plan, ideal_weight, calories_needed
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from io import BytesIO

import boto3
import json
import os
import requests

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fitops-secret")

# ---------- DATABASE ----------
_db_uri = None

def get_db_uri():
    global _db_uri

    if _db_uri:
        return _db_uri

    try:
        client_boto = boto3.client(
            "secretsmanager",
            region_name="eu-north-1"
        )

        secret = json.loads(
            client_boto.get_secret_value(
                SecretId="fitops-db-secret"
            )["SecretString"]
        )

        _db_uri = (
            f"mysql+pymysql://{secret['username']}:{secret['password']}@"
            f"{secret['host']}:{secret['port']}/{secret['dbname']}"
        )

        return _db_uri

    except Exception:
        return os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://fitops:fitops123@mysql:3306/fitopsdb"
        )


app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

with app.app_context():
    db.create_all()


# ---------- AUTH ----------

    result = {
        **plan,
        "bmi": bmi,
        "calories": calories,
        "ideal": ideal_weight(height)
    }

    session['report'] = result

    user = User.query.filter_by(
        username=session['user']
    ).first()

    if user:
        progress = Progress(
            user_id=user.id,
            bmi=bmi,
            weight=weight,
            calories=calories
        )

        db.session.add(progress)
        db.session.commit()

    return render_template(
        'result.html',
        result=result
    )


# ---------- LOGIN ----------
@app.route('/login',methods=['GET','POST'])
def login():

    if request.method=='POST':

        user = User.query.filter_by(
            username=request.form['username']
        ).first()

        if user and check_password_hash(
            user.password,
            request.form['password']
        ):

            session['user']=user.username
            return redirect('/')

    return render_template('login.html')


# ---------- REGISTER ----------
@app.route('/register',methods=['GET','POST'])
def register():

    if request.method=='POST':

        existing=User.query.filter_by(
            username=request.form['username']
        ).first()

        if existing:
            return "Username already exists"

        user=User(
            username=request.form['username'],
            password=generate_password_hash(
                request.form['password']
            )
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


# ---------- CHATBOT ----------
@app.route('/chat',methods=['POST'])
@login_required
def chat():

    msg=request.json.get("message")

    try:

        response=requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model":"llama3",
                "prompt":f"You are a fitness expert coach. Answer:\n{msg}",
                "stream":False
            }
        )

        reply=response.json().get(
            "response",
            "No response"
        )

    except Exception as e:

        reply=f"Error: {str(e)}"

    return jsonify({"reply":reply})


# ---------- PROGRESS ----------
@app.route('/progress-data')
@login_required
def progress_data():

    user=User.query.filter_by(
        username=session['user']
    ).first()

    records=Progress.query.filter_by(
        user_id=user.id
    ).all()

    return {
        "weights":[r.weight for r in records],
        "dates":[r.recorded_at.strftime('%Y-%m-%d') for r in records]
    }


# ---------- PDF ----------
@app.route('/download')
@login_required
def download():

    data=session.get('report')

    buffer=BytesIO()

    doc=SimpleDocTemplate(buffer)
    styles=getSampleStyleSheet()

    content=[
        Paragraph("FitOps AI Report",styles['Title']),
        Spacer(1,10)
    ]

    for k,v in data.items():
        content.append(
            Paragraph(f"<b>{k.upper()}</b>: {v}",styles['Normal'])
        )
        content.append(Spacer(1,8))

    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='fitops_report.pdf'
    )


@app.route('/health')
def health():
    return {"status":"ok"},200


@app.after_request
def headers(response):

    response.headers['X-Frame-Options']='DENY'
    response.headers['X-Content-Type-Options']='nosniff'

    return response


if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
