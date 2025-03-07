from flask_blog.repositories.blog_post_repository import BlogPostRepository
from flask_blog.repositories.tag_repository import TagRepository
from flask_blog.services.blog_post_service import BlogPostService
from flask_blog.services.tag_service import TagService
from flask import flash, redirect, render_template, request, url_for
from flask import Blueprint
from flask_blog.blogs.models import BlogPost
from flask_login import current_user, login_required
from .forms import BlogPostForm
from werkzeug.exceptions import Forbidden

blogs_bp = Blueprint("blogs", __name__, template_folder="templates")
blog_post_repo = BlogPostRepository()
tag_repo = TagRepository()
blog_service = BlogPostService(blog_post_repo, tag_repo)
tag_service = TagService(tag_repo)

@blogs_bp.get("/")
def index():
    blogs = blog_service.get_recent_blogs()
    tags = tag_service.get_all()

    return render_template("index.html", blogs=blogs, tags=tags)

@blogs_bp.get("/blog")
def blogs():
    page = request.args.get("page", 1, type=int)
    search = request.args.get('search')
    tag_slugs = request.args.get('tag')
    tag_slugs_list = tag_slugs.split(',') if tag_slugs else []

    blogs = blog_service.get_paginated_blogs(tag_slugs_list, search, page)

    tags = tag_service.get_all()

    return render_template("blogs.html", blogs=blogs, tags=tags, selected_tags=tag_slugs_list)

@blogs_bp.get("/blog/<int:blog_id>")
def detail(blog_id):
    blog = blog_service.get_blog_by_id(blog_id)
    related_blogs = blog_service.get_related_blogs(blog)

    return render_template("detail.html", blog=blog, related_blogs=related_blogs)

@blogs_bp.get("/blog/my")
@login_required
def my_blogs():
    blogs = blog_service.get_paginated_user_blogs(current_user)

    return render_template("my_blogs.html", blogs=blogs)

@blogs_bp.route("/blog/create", methods=["GET", "POST"])
@login_required
def create():
    form = BlogPostForm(request.form)

    if form.validate_on_submit():
        blog = blog_service.create_blog_post(
            title=form.title.data,
            content=form.content.data,
            image=request.files.get("image"),
            author=current_user,
            tag_ids=form.tags.data
        )

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
        blog_service.update_blog_post(
            blog_id=blog.id,
            title=form.title.data,
            content=form.content.data,
            image=request.files.get("image"),
            tag_ids=form.tags.data
        )

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
        blog_service.delete_blog_post(blog_id)

        flash("Blog deleted successfully!", "success")
        return redirect(url_for("blogs.my_blogs"))

    return render_template("delete.html", blog=blog)