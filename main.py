from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
from models import db, User, Product, Transaction
from forms import LoginForm, RegistrationForm, ProductForm
from utils import get_stripe_publishable_key, create_stripe_checkout_session
import random
from email_validator import validate_email, EmailNotValidError
import logging

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    google_maps_api_key = app.config['GOOGLE_MAPS_API_KEY']
    return render_template('index.html', google_maps_api_key=google_maps_api_key)

@app.route('/marketplace')
def marketplace():
    products = Product.query.all()
    return render_template('marketplace.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            validate_email(form.email.data)
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already registered. Please use a different email.', 'error')
                return render_template('register.html', form=form)
            
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            try:
                db.session.commit()
                logger.info(f"New user registered: {new_user.email}")
                flash('Your account has been created! You are now able to log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during user registration: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'error')
        except EmailNotValidError as e:
            flash(str(e), 'error')
    return render_template('register.html', form=form)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('The form has expired. Please try again.', 'error')
    return redirect(url_for('register'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data, seller_id=current_user.id)
        db.session.add(product)
        db.session.commit()
        flash('Your product has been created!', 'success')
        return redirect(url_for('marketplace'))
    return render_template('create_product.html', form=form)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/checkout/<int:product_id>', methods=['POST'])
@login_required
def checkout(product_id):
    product = Product.query.get_or_404(product_id)
    session = create_stripe_checkout_session(product)
    return redirect(session.url, code=303)

@app.route('/api/produce_data')
def produce_data():
    # Generate more realistic mock data for produce availability
    produce_types = [
        "Tomatoes", "Lettuce", "Carrots", "Cucumbers", "Peppers",
        "Squash", "Strawberries", "Herbs", "Onions", "Potatoes"
    ]
    
    data = []
    for _ in range(20):  # Generate 20 random data points
        lat = random.uniform(40.6, 40.8)  # Latitude range for New York City
        lng = random.uniform(-74.1, -73.9)  # Longitude range for New York City
        produce = random.choice(produce_types)
        price = round(random.uniform(1.5, 5.99), 2)
        organic = random.choice([True, False])
        
        data.append({
            "lat": lat,
            "lng": lng,
            "name": produce,
            "price": price,
            "organic": organic
        })
    
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
