from flask_wtf import FlaskForm
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class PasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=4, max=80)])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Confirm Password Reset")
