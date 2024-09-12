from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired


class NewJobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    submit = SubmitField('Save Job')


class SearchForm(FlaskForm):
    search = StringField('Query', validators=[DataRequired()])
    submit = SubmitField('Search')
