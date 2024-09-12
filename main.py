from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse
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

# ... (previous routes remain the same)

@app.route('/educational_resources')
def educational_resources():
    resources = [
        {
            'title': 'Urban Farming Basics',
            'description': 'Learn the fundamentals of urban farming and how to get started.',
            'link': '/urban-farming-basics',
            'image': 'urban_farming.jpg'
        },
        {
            'title': 'Sustainable Gardening Practices',
            'description': 'Discover eco-friendly gardening techniques for a greener future.',
            'link': '/sustainable-gardening',
            'image': 'sustainable_gardening.jpg'
        },
        {
            'title': 'Seasonal Planting Guide',
            'description': 'Know what to plant and when for optimal growth in your region.',
            'link': '/seasonal-planting-guide',
            'image': 'seasonal_planting.jpg'
        },
        {
            'title': 'Composting 101',
            'description': 'Turn your kitchen scraps into nutrient-rich soil for your garden.',
            'link': '/composting-101',
            'image': 'composting.jpg'
        },
        {
            'title': 'Pest Management for Urban Gardens',
            'description': 'Learn how to protect your plants from common urban pests naturally.',
            'link': '/pest-management',
            'image': 'pest_management.jpg'
        },
        {
            'title': 'Vertical Gardening Techniques',
            'description': 'Maximize your space with innovative vertical gardening methods.',
            'link': '/vertical-gardening',
            'image': 'vertical_gardening.jpg'
        },
        {
            'title': 'Hydroponics for Beginners',
            'description': 'Get started with soil-less gardening using hydroponics.',
            'link': '/hydroponics-beginners',
            'image': 'hydroponics.jpg'
        },
        {
            'title': 'Urban Beekeeping',
            'description': 'Learn how to keep bees in an urban environment and promote pollination.',
            'link': '/urban-beekeeping',
            'image': 'beekeeping.jpg'
        }
    ]
    return render_template('educational_resources.html', resources=resources)

@app.route('/educational_resources/<topic>')
def educational_topic(topic):
    # This is a placeholder for individual educational resource pages
    # In a full implementation, you would fetch the specific content for each topic
    return render_template('educational_topic.html', topic=topic)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
