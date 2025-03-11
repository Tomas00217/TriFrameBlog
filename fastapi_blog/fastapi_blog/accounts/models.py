from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class EmailUser(SQLModel, table=True):
    __tablename__ = "email_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=100)
    blog_posts: List["BlogPost"] = Relationship(back_populates="author")