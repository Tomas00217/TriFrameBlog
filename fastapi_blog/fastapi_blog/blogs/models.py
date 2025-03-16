from datetime import datetime, timezone
from typing import List, Optional
from fastapi import Request
from fastapi_blog.accounts.models import EmailUser
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import event
from slugify import slugify

class BlogPostTag(SQLModel, table=True):
    __tablename__ = "blogpost_tag"

    blogpost_id: int = Field(foreign_key="blog_post.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)

class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=50)
    slug: Optional[str] = Field(default=None, unique=True, max_length=60)

    blog_posts: List["BlogPost"] = Relationship(
        back_populates="tags", link_model=BlogPostTag
    )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
    
    async def __admin_repr__(self, request: Request):
        return self.name

@event.listens_for(Tag, "before_insert")
def generate_slug(mapper, connection, target):
    if not target.slug:
        target.slug = slugify(target.name)

class BlogPost(SQLModel, table=True):
    __tablename__ = "blog_post"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    content: str
    image: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    author: Optional[EmailUser] = Relationship(back_populates="blog_posts")
    author_id: int = Field(foreign_key="email_user.id")
    tags: List[Tag] = Relationship(back_populates="blog_posts", link_model=BlogPostTag)

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title
