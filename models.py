from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import func

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20))
    subscription_tier = db.Column(db.String(20), default='free')
    subscription_start_date = db.Column(db.DateTime)
    subscription_end_date = db.Column(db.DateTime)
    last_payment_date = db.Column(db.DateTime)
    mrr = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def start_subscription(self, tier, price):
        self.subscription_tier = tier
        self.subscription_start_date = datetime.utcnow()
        self.subscription_end_date = self.subscription_start_date + timedelta(days=30)
        self.last_payment_date = self.subscription_start_date
        self.mrr = price

    def renew_subscription(self):
        if self.subscription_tier != 'free':
            self.last_payment_date = datetime.utcnow()
            self.subscription_end_date = self.last_payment_date + timedelta(days=30)

    def cancel_subscription(self):
        self.subscription_tier = 'free'
        self.subscription_end_date = datetime.utcnow()
        self.mrr = 0.0

    def calculate_user_mrr(self):
        if self.subscription_tier == 'free':
            return 0.0
        elif datetime.utcnow() > self.subscription_end_date:
            return 0.0
        else:
            return self.mrr

    @staticmethod
    def calculate_total_mrr():
        return db.session.query(func.sum(User.mrr)).scalar() or 0.0

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Subscription {self.name} - ${self.price}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50))
    is_organic = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(255))
    image_url = db.Column(db.String(255))

    seller = db.relationship('User', backref='products')

    def calculate_total_price(self, user):
        base_price = self.price
        if user.subscription_tier == 'free':
            transaction_fee = base_price * 0.05  # 5% transaction fee for free users
        elif user.subscription_tier == 'pro':
            transaction_fee = base_price * 0.03  # 3% transaction fee for pro users
        else:  # Premium users
            transaction_fee = base_price * 0.01  # 1% transaction fee for premium users
        return base_price + transaction_fee