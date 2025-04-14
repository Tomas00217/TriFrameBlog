from blogs.models import BlogPost, Tag
from .forms import BlogPostForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def index(request):
    blogs = BlogPost.objects.recent()
    tags = Tag.objects.all()

    return render(request, "blogs/index.html", {"blogs": blogs, "tags": tags})

def blogs(request):
    tag_slugs = request.GET.get('tag', '')
    search = request.GET.get('search')

    tag_slugs_list = tag_slugs.split(',') if tag_slugs else []
    blog_list = BlogPost.objects.with_tags(tag_slugs_list).search_by_title(search)
    tags = Tag.objects.all()

    paginator = Paginator(blog_list, 6)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)

    return render(request, "blogs/blogs.html", {"blogs": blogs, "tags": tags, "selected_tags": tag_slugs_list})

def detail(request, blog_id: int):
    blog = get_object_or_404(BlogPost, pk=blog_id)
    related_blogs = BlogPost.objects.related_to(blog)

    return render(request, "blogs/detail.html", {"blog": blog, "related_blogs": related_blogs})

@login_required(login_url='/accounts/login/')
def my_blogs(request):
    blog_list = BlogPost.objects.by_author(request.user)

    paginator = Paginator(blog_list, 6)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)

    return render(request, "blogs/my_blogs.html", {"blogs": blogs})

@login_required(login_url='/accounts/login/')
def create(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(author=request.user)

            messages.success(request, "Blog created successfully.")
            return redirect("detail", blog_id=blog.pk)

        form.instance.image = None
        return render(request, "blogs/edit.html", {"form": form}, status=400)
    else:
        form = BlogPostForm()

    return render(request, "blogs/create.html", {"form": form})

@login_required(login_url='/accounts/login/')
def edit(request, blog_id: int):
    blog = get_object_or_404(BlogPost, pk=blog_id)
    blog_image = blog.image

    if request.user != blog.author and not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=blog)

        if form.is_valid():
            blog_post = form.save()

            messages.success(request, "Blog updated successfully.")
            return redirect("detail", blog_id=blog_post.pk)

        form.instance.image = blog_image
        return render(request, "blogs/edit.html", {"form": form, "blog": blog}, status=400)
    else:
        form = BlogPostForm(instance=blog)

    return render(request, "blogs/edit.html", {"form": form, "blog": blog})

@login_required(login_url='/accounts/login/')
def delete(request, blog_id: int):
    blog = get_object_or_404(BlogPost, pk=blog_id)

    if request.user != blog.author and not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        blog.delete()

        messages.success(request, "Blog deleted successfully.")
        return redirect("my_blogs")

    return render(request, "blogs/delete.html", {"blog": blog})