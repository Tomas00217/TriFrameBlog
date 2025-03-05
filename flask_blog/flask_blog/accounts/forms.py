from flask_blog.accounts.models import EmailUser
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    email = EmailField(
        "Email", validators=[DataRequired(), Email(message=None), Length(min=6, max=100)]
    )
    password1 = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=25)]
    )
    password2 = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password1", message="Passwords must match"),
        ],
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        user = EmailUser.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False

        return True

class UsernameUpdateForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=100)])