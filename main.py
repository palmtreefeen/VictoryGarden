from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Blueprint
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
from analytics import predict_demand_supply, get_market_insights, get_product_recommendations, get_optimal_price

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            validate_email(form.email.data)
        except EmailNotValidError:
            flash('Invalid email address.', 'error')
            return render_template('register.html', form=form)
        
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return render_template('register.html', form=form)
        
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

app.register_blueprint(auth, url_prefix='/auth')

@app.route('/')
def index():
    return render_template('index.html', google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@app.route('/marketplace')
def marketplace():
    products = Product.query.all()
    return render_template('marketplace.html', products=products)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/api/predict/<product_name>')
@login_required
def predict_product(product_name):
    try:
        prediction = predict_demand_supply(product_name)
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"Error predicting demand and supply for {product_name}: {str(e)}")
        return jsonify({"error": "An error occurred while predicting demand and supply"}), 500

@app.route('/api/market_insights/<product_name>')
@login_required
def market_insights(product_name):
    try:
        insights = get_market_insights(product_name)
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Error getting market insights for {product_name}: {str(e)}")
        return jsonify({"error": "An error occurred while fetching market insights"}), 500

@app.route('/api/recommendations/<product_name>')
@login_required
def product_recommendations(product_name):
    try:
        recommendations = get_product_recommendations(product_name)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting product recommendations for {product_name}: {str(e)}")
        return jsonify({"error": "An error occurred while fetching product recommendations"}), 500

@app.route('/api/optimal_price/<product_name>')
@login_required
def optimal_price(product_name):
    try:
        price_data = get_optimal_price(product_name)
        return jsonify(price_data)
    except Exception as e:
        logger.error(f"Error calculating optimal price for {product_name}: {str(e)}")
        return jsonify({"error": "An error occurred while calculating the optimal price"}), 500

@app.route('/analytics')
@login_required
def analytics_dashboard():
    products = Product.query.all()
    return render_template('analytics.html', products=products)

@app.route('/api/produce_data')
def produce_data():
    try:
        produce_list = [
            {"name": "Tomatoes", "lat": 40.7128, "lng": -74.0060, "price": 2.99, "organic": True},
            {"name": "Lettuce", "lat": 40.7282, "lng": -73.7949, "price": 1.99, "organic": False},
            {"name": "Carrots", "lat": 40.7489, "lng": -73.9680, "price": 1.49, "organic": True},
        ]
        return jsonify(produce_list)
    except Exception as e:
        logger.error(f"Error fetching produce data: {str(e)}")
        return jsonify({"error": "An error occurred while fetching produce data"}), 500

@app.route('/api/climate_zones')
def climate_zones():
    try:
        # More detailed mock data for climate and planting zones
        climate_data = [
            {"lat": 40.7128, "lng": -74.0060, "weight": 0.8, "zone": "7b", "temp_range": "5 to 10°F"},
            {"lat": 40.7282, "lng": -73.7949, "weight": 0.6, "zone": "7a", "temp_range": "0 to 5°F"},
            {"lat": 40.7489, "lng": -73.9680, "weight": 0.7, "zone": "7b", "temp_range": "5 to 10°F"},
            {"lat": 40.6782, "lng": -73.9442, "weight": 0.9, "zone": "7b", "temp_range": "5 to 10°F"},
            {"lat": 40.8075, "lng": -73.9619, "weight": 0.5, "zone": "7a", "temp_range": "0 to 5°F"},
            {"lat": 40.7587, "lng": -73.9787, "weight": 0.8, "zone": "7b", "temp_range": "5 to 10°F"},
            {"lat": 40.6872, "lng": -74.0229, "weight": 0.7, "zone": "7b", "temp_range": "5 to 10°F"},
            {"lat": 40.7829, "lng": -73.9654, "weight": 0.6, "zone": "7a", "temp_range": "0 to 5°F"},
            {"lat": 40.7174, "lng": -74.0121, "weight": 0.8, "zone": "7b", "temp_range": "5 to 10°F"},
            {"lat": 40.7605, "lng": -73.9933, "weight": 0.7, "zone": "7b", "temp_range": "5 to 10°F"},
        ]
        return jsonify(climate_data)
    except Exception as e:
        logger.error(f"Error fetching climate zone data: {str(e)}")
        return jsonify({"error": "An error occurred while fetching climate zone data"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
