from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Your password must match')])
    confirm = PasswordField('Confirm Password')
    type = SelectField('Type of Account', choices=[('s', 'Student'), ('e', 'Employer')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')
