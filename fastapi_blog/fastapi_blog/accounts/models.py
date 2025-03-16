from datetime import datetime, timezone
from typing import List, Optional
from fastapi import Request
from sqlmodel import Field, Relationship, SQLModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class EmailUser(SQLModel, table=True):
    __tablename__ = "email_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = Field(default=None, max_length=100)
    email: str = Field(unique=True, max_length=100)
    password_hash: str = Field(exclude=True)
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    blog_posts: List["BlogPost"] = Relationship(back_populates="author")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def __repr__(self):
        return self.email

    def __str__(self):
        return self.email

    async def __admin_repr__(self, request: Request):
        return self.email