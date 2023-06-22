from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app import User, Trips
from datetime import datetime

class RegistrationForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # password2 = PasswordField(
    #     'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class DestinationForm(FlaskForm):
    fly_from = StringField('Start City', validators=[DataRequired()], render_kw={"id": "fly_from_input", "autocomplete": "off"})
    fly_to = StringField('End City', validators=[DataRequired()], render_kw={"id": "fly_from_input", "autocomplete": "off"})
    date_from = DateField('Earliest Departure', validators=[DataRequired()])
    date_to = DateField('Arrival Date', validators=[DataRequired()])
    stops = IntegerField('Num of Stops', validators=[DataRequired()])
    budget = IntegerField('Budget', validators=[DataRequired()])
    planner = SelectMultipleField('Select Regions to include',
            choices=['OCEANIA_PLUS', 'SOUTH_EAST_ASIA','WESTERN_EU',
            'NORTH_AMERICA_EAST','NORTH_AMERICA_CENTRAL', 'NORTH_AMERICA_WEST',
            'MEX_CENTRAL_AMERICA','CHINA_CENTRAL_ASIA', 'INDIAN_SUB',
            'MIDDLE_EAST', 'SOUTH_AFRICA'])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


print(datetime.utcnow())
