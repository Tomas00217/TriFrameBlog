from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_blog.accounts.models import EmailUser
from flask_blog.repositories.email_user_repository import EmailUserRepository
from flask_blog.services.email_user_service import EmailUserService
from flask_login import current_user, login_required, login_user, logout_user
from .forms import LoginForm, RegisterForm, UsernameUpdateForm

accounts_bp = Blueprint("accounts", __name__, url_prefix="/accounts", template_folder="templates")
user_repo = EmailUserRepository()
user_service = EmailUserService(user_repo)

@accounts_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("blogs.index"))

    form = LoginForm(request.form)
    next_page = request.args.get("next")

    if form.validate_on_submit():
        user = user_service.get_user_by_email(form.email.data)

        if user and user.check_password(form.password.data):
            login_user(user)
            
            flash("Login successful.", "success")
            return redirect(next_page or url_for("blogs.index"))
        else:
            form.email.errors.append("Your email and password did not match. Please try again.")

    return render_template("login.html", form=form, next=next_page)

@accounts_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("blogs.index"))

    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user_service.register_user(form.email.data, form.password1.data)

        flash("Register successful.", "success")
        return redirect(url_for("accounts.login"))

    return render_template("register.html", form=form)

@accounts_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash("You were logged out.", "success")
    return redirect(url_for("blogs.index"))

@accounts_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UsernameUpdateForm(obj=current_user)

    if form.validate_on_submit():
        user_service.update_user(current_user, form.username.data)

        flash("Your username has been updated!", "success")
        return redirect(url_for("accounts.profile"))

    return render_template("profile.html", form=form)