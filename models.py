from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    progress = db.relationship('Progress', backref='user', lazy=True)


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    bmi = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Integer)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
