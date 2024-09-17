from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import db, User, Subscription, Transaction, Product
from sqlalchemy import func

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

@app.route('/marketplace')
def marketplace():
    products = Product.query.all()
    return render_template('marketplace.html', products=products)

@app.route('/educational_resources')
def educational_resources():
    # Add your educational resources logic here
    return render_template('educational_resources.html')

@app.route('/change_subscription', methods=['POST'])
@login_required
def change_subscription():
    new_tier = request.form.get('new_tier')
    if new_tier not in ['free', 'pro', 'premium']:
        flash('Invalid subscription tier.')
        return redirect(url_for('profile'))

    subscription = Subscription.query.filter_by(name=new_tier).first()
    if not subscription:
        flash('Subscription tier not found.')
        return redirect(url_for('profile'))

    current_user.start_subscription(new_tier, subscription.price)
    db.session.commit()

    flash(f'Your subscription has been updated to {new_tier}.')
    return redirect(url_for('profile'))

@app.route('/cancel_subscription', methods=['POST'])
@login_required
def cancel_subscription():
    current_user.cancel_subscription()
    db.session.commit()
    flash('Your subscription has been canceled.')
    return redirect(url_for('profile'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/admin/mrr_dashboard')
@login_required
def mrr_dashboard():
    if not current_user.is_authenticated or current_user.user_type != 'admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    mrr = User.calculate_total_mrr()
    arr = mrr * 12
    
    subscription_breakdown = db.session.query(User.subscription_tier, func.count(User.id)).group_by(User.subscription_tier).all()
    revenue_by_tier = db.session.query(Subscription.name, func.sum(User.mrr)).join(User, User.subscription_tier == Subscription.name).group_by(Subscription.name).all()

    return render_template('admin/mrr_dashboard.html', 
                           mrr=mrr,
                           arr=arr,
                           subscription_breakdown=subscription_breakdown,
                           revenue_by_tier=revenue_by_tier)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
