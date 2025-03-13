from fastapi_blog.forms import MyForm
from fastapi_blog.services.email_user_service import EmailUserService
from wtforms import EmailField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(MyForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(MyForm):
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

    async def validate(self, user_service: EmailUserService, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        user = await user_service.get_user_by_email(self.email.data)
        if user:
            self.email.errors.append("Email already registered")
            return False

        return True