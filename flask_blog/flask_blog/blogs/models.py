from datetime import datetime, timezone
from typing import Optional, List
from flask_blog.extensions import db
from sqlalchemy import DateTime, ForeignKey, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from slugify import slugify
from flask_blog.accounts.models import EmailUser

blogpost_tags = db.Table(
    "blogpost_tags",
    db.Column("blogpost_id", db.Integer, db.ForeignKey("blog_post.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    slug: Mapped[Optional[str]] = mapped_column(String(60), unique=True)

    def __repr__(self):
        return self.name

@event.listens_for(Tag, "before_insert")
def generate_slug(mapper, connection, target):
    if not target.slug:
        target.slug = slugify(target.name)

class BlogPost(db.Model):
    __tablename__ = "blog_post"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    image: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    tags: Mapped[List[Tag]] = relationship("Tag", secondary=blogpost_tags, backref="blog_posts")
    author_id: Mapped[int] = mapped_column(ForeignKey("email_user.id"))
    author: Mapped["EmailUser"] = relationship("EmailUser", backref="blog_posts")

    def __repr__(self):
        return self.title