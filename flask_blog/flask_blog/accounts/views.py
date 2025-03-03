from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_blog.accounts.models import EmailUser
from flask_login import current_user, login_required, login_user, logout_user
from flask_blog import db
from .forms import LoginForm, RegisterForm

accounts_bp = Blueprint("accounts", __name__, url_prefix="/accounts", template_folder="templates")

@accounts_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("blogs.index"))

    form = LoginForm(request.form)
    next_page = request.args.get("next")

    if form.validate_on_submit():
        user = EmailUser.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            
            flash("Login successful.", "success")
            return redirect(next_page or url_for("blogs.index"))
        else:
            form.email.errors.append("Your email and password did not match. Please try again.")

    return render_template("accounts/login.html", form=form, next=next_page)

@accounts_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("blogs.index"))

    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = EmailUser(email=form.email.data, password=form.password1.data)

        db.session.add(user)
        db.session.commit() 

        flash("Register successful.", "success")

        return redirect(url_for("accounts.login"))

    return render_template("accounts/register.html", form=form)

@accounts_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash("You were logged out.", "success")
    return redirect(url_for("blogs.index"))