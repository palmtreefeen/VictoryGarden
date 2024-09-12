# ... (previous imports and code remain the same)

from flask_login import login_required, current_user
from functools import wraps

# ... (previous routes and functions remain the same)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/revenue_dashboard')
@login_required
@admin_required
def revenue_dashboard():
    # Calculate total revenue from transaction fees
    total_revenue = db.session.query(db.func.sum(Transaction.fee)).scalar() or 0

    # Calculate revenue by subscription tier
    revenue_by_tier = db.session.query(
        User.subscription_tier,
        db.func.sum(Transaction.fee)
    ).join(Transaction, User.id == Transaction.buyer_id
    ).group_by(User.subscription_tier).all()

    # Get the number of users for each subscription tier
    users_by_tier = db.session.query(
        User.subscription_tier,
        db.func.count(User.id)
    ).group_by(User.subscription_tier).all()

    return render_template('admin/revenue_dashboard.html',
                           total_revenue=total_revenue,
                           revenue_by_tier=revenue_by_tier,
                           users_by_tier=users_by_tier)

# ... (rest of the file remains the same)
