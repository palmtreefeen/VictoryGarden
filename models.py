from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20))
    subscription_tier = db.Column(db.String(20), default='free')
    subscription_end_date = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_organic = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)  # New field for product category
    image_url = db.Column(db.String(200))  # New field for product image URL

    seller = db.relationship('User', backref=db.backref('products', lazy=True))

    def calculate_total_price(self, buyer):
        if buyer.subscription_tier == 'free':
            fee_percentage = 0.04
        elif buyer.subscription_tier == 'pro':
            fee_percentage = 0.02
        else:  # premium tier
            fee_percentage = 0.01

        transaction_fee = self.price * fee_percentage
        return self.price + transaction_fee

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('transactions', lazy=True))
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref=db.backref('purchases', lazy=True))
    seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('sales', lazy=True))
