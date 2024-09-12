from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('User Type', choices=[('buyer', 'Buyer'), ('seller', 'Seller'), ('vendor', 'Vendor')], validators=[DataRequired()])
    submit = SubmitField('Register')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    is_organic = BooleanField('Organic Product')
    submit = SubmitField('Create Product')

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Create Service')

class OnboardingForm(FlaskForm):
    experience = SelectField('Gardening Experience', choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')])
    interests = StringField('Gardening Interests (comma-separated)', validators=[DataRequired()])
    location = StringField('Location (City, State)', validators=[DataRequired()])
    garden_size = SelectField('Garden Size', choices=[('small', 'Small (0-100 sq ft)'), ('medium', 'Medium (100-500 sq ft)'), ('large', 'Large (500+ sq ft)')])
    soil_type = SelectField('Soil Type', choices=[('clay', 'Clay'), ('sandy', 'Sandy'), ('loamy', 'Loamy'), ('silt', 'Silt'), ('peat', 'Peat'), ('chalky', 'Chalky')])
    sunlight = SelectField('Sunlight Exposure', choices=[('full', 'Full Sun'), ('partial', 'Partial Sun'), ('shade', 'Shade')])
    watering_frequency = SelectField('Watering Frequency', choices=[('daily', 'Daily'), ('every_other_day', 'Every Other Day'), ('twice_a_week', 'Twice a Week'), ('weekly', 'Weekly')])
    preferred_products = StringField('Preferred Products to Grow (comma-separated)')
    organic_preference = BooleanField('Prefer Organic Products and Methods')
    climate_zone = StringField('USDA Hardiness Zone (if known)')
    goals = TextAreaField('Gardening Goals')
    challenges = TextAreaField('Current Gardening Challenges')
    submit = SubmitField('Complete Onboarding')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    category = SelectField('Category', choices=[('products', 'Products'), ('services', 'Services')])
    location = StringField('Location')
    submit = SubmitField('Search')
