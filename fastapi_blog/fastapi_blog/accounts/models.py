from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class EmailUser(SQLModel, table=True):
    __tablename__ = "email_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = Field(default=None, max_length=100)
    email: str = Field(unique=True, max_length=100)
    password_hash: str = Field(exclude=True)
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    blog_posts: List["BlogPost"] = Relationship(back_populates="author") # type: ignore