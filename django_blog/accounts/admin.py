from .forms import EmailUserChangeForm, EmailUserCreationForm
from .models import EmailUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

class EmailUserAdmin(UserAdmin):
    add_form = EmailUserCreationForm
    form = EmailUserChangeForm
    model = EmailUser
    ordering = ("email",)
    search_fields = ("email",)
    list_display = ("username", "email", "is_staff", "is_active")
    list_filter = ("username", "email", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

admin.site.register(EmailUser, EmailUserAdmin)