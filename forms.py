from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email


class RegistrationForm(FlaskForm):
    """Form for registering a new user."""

    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])


class LoginForm(FlaskForm):
    """Form for returning user to login to account."""

    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=40)]
    )

class FeedbackForm(FlaskForm):
    """Form for posting feedback."""

    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = StringField("Content", validators=[InputRequired()])
