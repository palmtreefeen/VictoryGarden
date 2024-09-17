from main import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@victorygarden.io').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@victorygarden.io',
                user_type='admin'
            )
            admin.password_hash = generate_password_hash('admin123')  # Set a secure password in production
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")

        # Verify admin user
        admin = User.query.filter_by(email='admin@victorygarden.io').first()
        if admin and admin.user_type == 'admin':
            print(f"Admin user verified: {admin.username}, {admin.email}, {admin.user_type}")
        else:
            print("Failed to verify admin user.")

if __name__ == '__main__':
    create_admin_user()
