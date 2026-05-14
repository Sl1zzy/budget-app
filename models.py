from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='author', lazy=True, 
                                   cascade='all, delete-orphan')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' или 'expense'
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))
    receipt_path = db.Column(db.String(200))  # Путь к загруженному чеку
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Transaction('{self.type}', '{self.amount}', '{self.date_posted}')"