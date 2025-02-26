from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("blog/", views.blogs, name="blogs"),
    path("blog/<int:blog_id>", views.detail, name="detail"),
    path("blog/create", views.create, name="create"),
    path("blog/my", views.my_blogs, name="my_blogs"),
]