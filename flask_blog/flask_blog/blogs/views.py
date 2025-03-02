from flask import render_template
from flask import Blueprint
from flask_blog.blogs.models import Tag, BlogPost

blogs_bp = Blueprint("blogs", __name__, template_folder="templates")

@blogs_bp.get("/")
def index():
    blogs = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(3).all()
    tags = Tag.query.all()

    return render_template("index.html", blogs=blogs, tags=tags)

@blogs_bp.get("/blogs")
def blogs():
    return render_template("blogs.html")