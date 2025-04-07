from typing import Any
from wtforms import Form, PasswordField
from flask_blog.admin import AdminModelView
from wtforms.validators import DataRequired

class EmailUserAdminView(AdminModelView):
    column_list = ("username", "email", "is_active", "is_staff", "created_at")
    form_excluded_columns = ["password_hash"]


    def on_model_change(self, form: Form, model: Any, is_created: bool):
        if form.password.data:
            model.set_password(form.password.data)

        super(EmailUserAdminView, self).on_model_change(form, model, is_created)

    def get_edit_form(self):
        form = super(EmailUserAdminView, self).get_edit_form()
        form.password = PasswordField("Password")

        return form

    def get_create_form(self):
        form = super(EmailUserAdminView, self).get_create_form()
        form.password = PasswordField("Password", validators=[DataRequired()])
        return form
