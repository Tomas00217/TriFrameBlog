import bleach
import cloudinary.uploader
from flask import flash, redirect, render_template, request, url_for
from flask import Blueprint
from flask_blog import db
from flask_blog.blogs.models import Tag, BlogPost
from flask_login import current_user, login_required
from sqlalchemy import func
from .forms import BlogPostForm
from werkzeug.exceptions import Forbidden

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
            blog_list = blog_list.filter(BlogPost.tags.any(Tag.slug == tag_slug))

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

@blogs_bp.route("/blog/create", methods=["GET", "POST"])
@login_required
def create():
    form = BlogPostForm(request.form)

    if form.validate_on_submit():
        content = bleach.clean(
            form.content.data,
            tags=["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"],
            attributes={"a": ["href", "target"], "span": ["class", "contenteditable"]},
        )

        image_url = None
        if "image" in request.files and request.files["image"].filename:
            image_file = request.files["image"]
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result["secure_url"]

        blog = BlogPost(
            title = form.title.data,
            content = content,
            image = image_url,
            author = current_user
        )

        db.session.add(blog)
        db.session.flush()

        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        blog.tags.extend(selected_tags)

        db.session.commit()

        flash("Blog created successfully!", "success")
        return redirect(url_for("blogs.detail", blog_id=blog.id))

    return render_template("create.html", form=form)

@blogs_bp.route("/blog/<int:blog_id>/edit", methods=["GET", "POST"])
@login_required
def edit(blog_id):
    blog = BlogPost.query.get_or_404(blog_id)

    if current_user != blog.author and not current_user.is_staff:
        raise Forbidden

    form = BlogPostForm(obj=blog)

    if request.method == "GET":
        form.tags.data = [tag.id for tag in blog.tags]

    if form.validate_on_submit():
        blog.content = bleach.clean(
            form.content.data,
            tags=["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"],
            attributes={"a": ["href", "target"], "span": ["class", "contenteditable"]},
        )

        if "image" in request.files and request.files["image"].filename:
            image_file = request.files["image"]
            upload_result = cloudinary.uploader.upload(image_file)
            blog.image = upload_result["secure_url"]

        blog.title = form.title.data

        print(form.tags.data)
        selected_tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
        blog.tags = selected_tags

        db.session.commit()

        flash("Blog updated successfully!", "success")
        return redirect(url_for("blogs.detail", blog_id=blog.id))

    return render_template("edit.html", form=form, blog=blog)

@blogs_bp.route("/blog/<int:blog_id>/delete", methods=["GET", "POST"])
@login_required
def delete(blog_id):
    blog = BlogPost.query.get_or_404(blog_id)

    if current_user != blog.author and not current_user.is_staff:
        raise Forbidden
    
    if request.method == "POST":
        db.session.delete(blog)
        db.session.commit()

        flash("Blog deleted successfully!", "success")
        return redirect(url_for("blogs.my_blogs"))

    return render_template("delete.html", blog=blog)