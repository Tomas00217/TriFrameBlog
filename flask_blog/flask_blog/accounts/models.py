from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from flask_blog import bcrypt, db
from flask_login import UserMixin

class EmailUser(UserMixin, db.Model):
    __tablename__ = 'email_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    def __init__(self, email: str, password: str):
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return f"<EmailUser {self.email}>"

    def set_password(self, password):
        """Hashes and sets the password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks the password hash"""
        return bcrypt.check_password_hash(self.password_hash, password)