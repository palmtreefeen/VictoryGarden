from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.urls import url_parse
from models import db, User, Product, Transaction
from forms import LoginForm, RegistrationForm, ProductForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///victorygardenio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/marketplace')
def marketplace():
    products = Product.query.all()
    return render_template('marketplace.html', products=products)

@app.route('/marketplace/<category>')
def marketplace_category(category):
    products = Product.query.filter_by(category=category).all()
    return render_template('marketplace_category.html', category=category, products=products)

@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            seller_id=current_user.id,
            is_organic=form.is_organic.data,
            tags=form.tags.data,
            category=form.category.data,
            image_url=form.image_url.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Your product has been created!')
        return redirect(url_for('marketplace'))
    return render_template('create_product.html', title='Create Product', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
