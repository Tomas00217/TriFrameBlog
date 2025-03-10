from flask_blog.container import container
from flask import abort, flash, redirect, render_template, request, url_for
from flask import Blueprint
from flask_login import current_user, login_required
from .forms import BlogPostForm
from werkzeug.exceptions import Forbidden

blogs_bp = Blueprint("blogs", __name__, template_folder="templates")
blog_service = container.blog_service
tag_service = container.tag_service

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
    try:
        blog = blog_service.get_blog_by_id(blog_id)
        related_blogs = blog_service.get_related_blogs(blog)

        return render_template("detail.html", blog=blog, related_blogs=related_blogs)
    except ValueError as e:
        abort(404, description=str(e))

@blogs_bp.get("/blog/my")
@login_required
def my_blogs():
    page = request.args.get("page", 1, type=int)
    blogs = blog_service.get_paginated_user_blogs(current_user, page)

    return render_template("my_blogs.html", blogs=blogs)

@blogs_bp.route("/blog/create", methods=["GET", "POST"])
@login_required
def create():
    form = BlogPostForm(formdata=request.form, tag_service=tag_service)

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
    try:
        blog = blog_service.get_blog_by_id(blog_id)

        if current_user != blog.author and not current_user.is_staff:
            raise Forbidden

        form = BlogPostForm(obj=blog, tag_service=tag_service)

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
    except ValueError as e:
        abort(404, description=str(e))

@blogs_bp.route("/blog/<int:blog_id>/delete", methods=["GET", "POST"])
@login_required
def delete(blog_id):
    try:
        blog = blog_service.get_blog_by_id(blog_id)

        if current_user != blog.author and not current_user.is_staff:
            raise Forbidden
        
        if request.method == "POST":
            blog_service.delete_blog_post(blog_id)

            flash("Blog deleted successfully!", "success")
            return redirect(url_for("blogs.my_blogs"))

        return render_template("delete.html", blog=blog)
    except ValueError as e:
        abort(404, description=str(e))