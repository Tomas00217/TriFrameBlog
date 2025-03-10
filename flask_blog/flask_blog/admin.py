from flask import flash, redirect, request, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for("accounts.login", next=request.url))
        return super().index()

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_staff

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be logged in to access the admin panel.", "danger")
        return redirect(url_for("accounts.login", next=request.url))