from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField
from wtforms.fields.simple import TextAreaField, BooleanField


class StudentProfileForm(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone = StringField('Phone Number')
    photo = FileField()
    delete_photo = BooleanField('Delete Photo')
    education = TextAreaField('Education Timeline')
    experience = TextAreaField('Work Experience Timeline')
    skills = StringField('Skills')
    submit = SubmitField('Save Profile')


class EmployerProfileForm(FlaskForm):
    name = StringField('Name')
    email = StringField('Email')
    website = StringField('Website')
    photo = FileField()
    delete_photo = BooleanField('Delete Photo')
    submit = SubmitField('Save Profile')
