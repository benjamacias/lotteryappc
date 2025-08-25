from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime


db = SQLAlchemy()


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    document = db.Column(db.String(50), nullable=False)
    debts = db.relationship("Debt", backref="client", cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="client", cascade="all, delete-orphan")
    movements = db.relationship("Movement", backref="client", cascade="all, delete-orphan")

    @property
    def total_debt(self) -> float:
        debt_total = sum(d.amount for d in self.debts)
        payment_total = sum(p.amount for p in self.payments)
        return debt_total - payment_total


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Float, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    movements = db.relationship("Movement", backref="user")


class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    action = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float)
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
