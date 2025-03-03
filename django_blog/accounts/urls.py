from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("login/", views.email_login, name="login"),
    path("register/", views.register, name="register"),
]