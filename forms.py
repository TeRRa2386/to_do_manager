from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, DateField, TimeField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired


class TodoForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    add = SubmitField('Add To Do')


class SignUpForm(FlaskForm):

    first = StringField('Name', validators=[DataRequired()])
    last = StringField('Last name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SignInForm(FlaskForm):

    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


