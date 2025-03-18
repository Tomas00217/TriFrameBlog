from fastapi_blog.services.email_user_service import EmailUserService
from starlette_wtf import StarletteForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(StarletteForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(StarletteForm):
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

class UsernameUpdateForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=100)])