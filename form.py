from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, URL, Email


# Create a Registration Form
class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    login = SubmitField("Login")


class AddTaskForm(FlaskForm):
    name = StringField("Task Name:", validators=[DataRequired()])
    start_date = DateField('Start Date (YYYY-MM-DD)')
    due_date = DateField('Due Date (YYYY-MM-DD)')
    priority = SelectField('Priority:', choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    save = SubmitField("Save")
