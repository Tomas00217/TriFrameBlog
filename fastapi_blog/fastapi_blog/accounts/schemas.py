from fastapi_blog.schemas import CSRFFormModel
from pydantic import EmailStr, Field, field_validator, model_validator

class LoginForm(CSRFFormModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class RegisterFormModel(CSRFFormModel):
    email: EmailStr = Field(..., max_length=100)
    password1: str = Field(...)
    password2: str = Field(...)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Email should have at least 6 characters")
        return v
    
    @field_validator('password1')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password should have at least 8 characters")
        if len(v) > 25:
            raise ValueError("Password should not exceed 25 characters")
        return v
    
    @model_validator(mode='after')
    def passwords_match(self):
        if self.password1 != self.password2:
            raise ValueError("Passwords must match")
        return self

class UsernameUpdateForm(CSRFFormModel):
    username: str = Field(...)