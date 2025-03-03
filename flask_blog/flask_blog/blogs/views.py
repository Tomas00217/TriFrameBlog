from flask import render_template, request
from flask import Blueprint
from flask_blog.blogs.models import Tag, BlogPost
from flask_login import current_user, login_required
from sqlalchemy import func

blogs_bp = Blueprint("blogs", __name__, template_folder="templates")

@blogs_bp.get("/")
def index():
    blogs = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(3).all()
    tags = Tag.query.all()

    return render_template("index.html", blogs=blogs, tags=tags)

@blogs_bp.get("/blog")
def blogs():
    blog_list = BlogPost.query.join(BlogPost.tags)
    tags = Tag.query.all()
    tag_slugs = request.args.get('tag')

    tag_slugs_list = []

    if tag_slugs:
        tag_slugs_list = tag_slugs.split(',')
        for tag_slug in tag_slugs_list:
            blog_list = blog_list.filter(Tag.slug == tag_slug)

    search = request.args.get('search')

    if search:
        blog_list = blog_list.filter(BlogPost.title.contains(search))

    blog_list = blog_list.distinct().order_by(BlogPost.created_at.desc())
    blogs = blog_list.paginate(per_page=6)

    return render_template("blogs.html", blogs=blogs, tags=tags, selected_tags=tag_slugs_list)

@blogs_bp.get("/blog/<int:blog_id>")
def detail(blog_id):
    blog = BlogPost.query.get_or_404(blog_id)
    related_blogs = (
        BlogPost.query
        .join(BlogPost.tags)
        .filter(Tag.id.in_([tag.id for tag in blog.tags]))
        .filter(BlogPost.id != blog.id)
        .distinct(BlogPost.id)
        .order_by(BlogPost.id, func.random())
        .limit(3)
        .all()
        )

    return render_template("detail.html", blog=blog, related_blogs=related_blogs)

@blogs_bp.get("/blog/my")
@login_required
def my_blogs():
    blog_list = BlogPost.query.filter_by(author=current_user)
    blogs = blog_list.paginate(per_page=6)

    return render_template("my_blogs.html", blogs=blogs)