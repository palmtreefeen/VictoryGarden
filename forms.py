from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    is_organic = BooleanField('Organic Product')
    tags = StringField('Tags (comma-separated)', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('gardening_tools', 'Gardening Tools'),
        ('gardening_kits', 'Gardening Kits'),
        ('urban_systems', 'Urban Systems'),
        ('seeds', 'Seeds'),
        ('plants', 'Plants'),
        ('soil_fertilizers', 'Soil and Fertilizers')
    ], validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[DataRequired()])
    submit = SubmitField('Create Product')
