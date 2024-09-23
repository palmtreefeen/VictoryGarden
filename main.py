from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from models import db, User, Subscription, Transaction
from sqlalchemy import func
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/marketplace')
def marketplace():
    # Add logic to fetch products or other marketplace data
    products = []  # Replace this with actual product data
    return render_template('marketplace.html', products=products)

@app.route('/educational_resources')
def educational_resources():
    # Add logic to fetch educational resources
    resources = []  # Replace this with actual resource data
    return render_template('educational_resources.html', resources=resources)

@app.route('/admin/mrr_dashboard')
@login_required
def mrr_dashboard():
    if not current_user.is_authenticated or current_user.user_type != 'admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    total_mrr = User.calculate_total_mrr()
    total_users = User.query.count()
    paying_users = User.query.filter(User.subscription_tier != 'free').count()
    arpu = total_mrr / total_users if total_users > 0 else 0

    subscription_breakdown = db.session.query(
        User.subscription_tier,
        func.count(User.id).label('count'),
        func.sum(User.mrr).label('revenue')
    ).group_by(User.subscription_tier).all()

    return render_template('admin/mrr_dashboard.html',
                           total_mrr=total_mrr,
                           total_users=total_users,
                           paying_users=paying_users,
                           arpu=arpu,
                           subscription_breakdown=subscription_breakdown)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
