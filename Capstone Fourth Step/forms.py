from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from wtforms_alchemy import QuerySelectMultipleField



class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    #password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    job_title = StringField('Job Title', validators=[DataRequired()])
    submit = SubmitField("Sign Up!")


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    submit = SubmitField("Login!")


class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    #password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    job_title = StringField('Job Title', validators=[DataRequired()])


class AddIntForm(FlaskForm):
    """Form to add interviews"""
    choices = QuerySelectMultipleField("Choices")


class NewTaskFormApp(FlaskForm):
    notes = StringField(' New Task', validators=[DataRequired()])
#    choices = QuerySelectMultipleField("Choices")

class NewTaskFormRec(FlaskForm):
    notes = StringField(' New Task', validators=[DataRequired()])
#    choices = QuerySelectMultipleField("Choices")


class RecruiterEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField("Add New Recruiter!")