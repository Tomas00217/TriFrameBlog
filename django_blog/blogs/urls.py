from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("blogs/", views.blogs, name="blogs"),
    path("blogs/<int:blog_id>", views.detail, name="detail"),
    path("blogs/create", views.create, name="create"),
    path("blogs/<int:blog_id>/edit", views.edit, name="edit"),
    path("blogs/<int:blog_id>/delete", views.delete, name="delete"),
    path("blogs/my", views.my_blogs, name="my_blogs"),
]