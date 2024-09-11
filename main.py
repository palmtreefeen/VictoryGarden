from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
from models import db, User, Product, Transaction, Service, Booking, Subscription
from forms import LoginForm, RegistrationForm, ProductForm, ServiceForm
from utils import get_stripe_publishable_key, create_stripe_checkout_session
import random
from email_validator import validate_email, EmailNotValidError
import logging
from analytics import predict_demand_supply, get_market_insights, get_product_recommendations, get_optimal_price
from datetime import datetime, timedelta

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
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, user_type=form.user_type.data)
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

@app.route('/buyer_portal')
@login_required
def buyer_portal():
    if current_user.user_type != 'buyer':
        flash('Access denied. This portal is for buyers only.', 'error')
        return redirect(url_for('index'))
    products = Product.query.all()
    orders = Transaction.query.filter_by(buyer_id=current_user.id).all()
    return render_template('buyer_portal.html', products=products, orders=orders)

@app.route('/seller_portal')
@login_required
def seller_portal():
    if current_user.user_type != 'seller':
        flash('Access denied. This portal is for sellers only.', 'error')
        return redirect(url_for('index'))
    products = Product.query.filter_by(seller_id=current_user.id).all()
    sales = Transaction.query.join(Product).filter(Product.seller_id == current_user.id).all()
    return render_template('seller_portal.html', products=products, sales=sales)

@app.route('/vendor_portal')
@login_required
def vendor_portal():
    if current_user.user_type != 'vendor':
        flash('Access denied. This portal is for vendors only.', 'error')
        return redirect(url_for('index'))
    services = Service.query.filter_by(vendor_id=current_user.id).all()
    bookings = Booking.query.filter_by(vendor_id=current_user.id).all()
    return render_template('vendor_portal.html', services=services, bookings=bookings)

@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
    if current_user.user_type != 'seller':
        flash('Access denied. Only sellers can create products.', 'error')
        return redirect(url_for('index'))
    
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            seller_id=current_user.id
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product created successfully.', 'success')
        return redirect(url_for('seller_portal'))
    return render_template('create_product.html', form=form)

@app.route('/create_service', methods=['GET', 'POST'])
@login_required
def create_service():
    if current_user.user_type != 'vendor':
        flash('Access denied. Only vendors can create services.', 'error')
        return redirect(url_for('index'))
    
    form = ServiceForm()
    if form.validate_on_submit():
        new_service = Service(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            vendor_id=current_user.id
        )
        db.session.add(new_service)
        db.session.commit()
        flash('Service created successfully.', 'success')
        return redirect(url_for('vendor_portal'))
    return render_template('create_service.html', form=form)

@app.route('/subscriptions')
def subscriptions():
    subscriptions = Subscription.query.all()
    return render_template('subscriptions.html', subscriptions=subscriptions)

@app.route('/subscribe/<int:subscription_id>', methods=['POST'])
@login_required
def subscribe(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    current_user.subscription_tier = subscription.name
    current_user.subscription_start_date = datetime.utcnow()
    current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    flash(f'You have successfully subscribed to the {subscription.name} tier.', 'success')
    return redirect(url_for('profile'))

@app.route('/cancel_subscription', methods=['POST'])
@login_required
def cancel_subscription():
    current_user.subscription_tier = 'free'
    current_user.subscription_end_date = datetime.utcnow()
    db.session.commit()
    flash('Your subscription has been canceled.', 'info')
    return redirect(url_for('profile'))

def add_default_subscriptions():
    subscriptions = [
        {
            'name': 'Free',
            'price': 0,
            'features': 'Basic access, Higher transaction fees'
        },
        {
            'name': 'Pro',
            'price': 9.99,
            'features': 'Lower transaction fees, Priority support, Advanced analytics'
        },
        {
            'name': 'Premium',
            'price': 19.99,
            'features': 'Lowest transaction fees, 24/7 support, Advanced analytics, Exclusive vendor offers'
        }
    ]

    for sub in subscriptions:
        existing_subscription = Subscription.query.filter_by(name=sub['name']).first()
        if not existing_subscription:
            new_subscription = Subscription(name=sub['name'], price=sub['price'], features=sub['features'])
            db.session.add(new_subscription)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_default_subscriptions()
    app.run(host='0.0.0.0', port=5000)
