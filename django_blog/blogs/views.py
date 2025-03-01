import bleach
from blogs.models import BlogPost, Tag
from .forms import BlogPostForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def index(request):
    blogs = BlogPost.objects.order_by("-created_at")[:3]
    tags = Tag.objects.all()

    return render(request, "blogs/index.html", {"blogs": blogs, "tags": tags})

def blogs(request):
    blog_list = BlogPost.objects.all()
    tags = Tag.objects.all()
    tag_slugs = request.GET.get('tag', '')
    tag_slugs_list = []

    if tag_slugs:
        tag_slugs_list = tag_slugs.split(',')
        for tag_slug in tag_slugs_list:
            blog_list = blog_list.filter(tags__slug=tag_slug)

    search = request.GET.get('search')

    if search:
        blog_list = blog_list.filter(title__icontains=search).distinct()

    paginator = Paginator(blog_list, 6)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)

    return render(request, "blogs/blogs.html", {"blogs": blogs, "tags": tags, "selected_tags": tag_slugs_list})

def detail(request, blog_id):
    blog = get_object_or_404(BlogPost, pk=blog_id)
    related_blogs = BlogPost.objects.filter(tags__in=blog.tags.all()).exclude(pk=blog.pk).distinct().order_by("?")[:3]

    return render(request, "blogs/detail.html", {"blog": blog, "related_blogs": related_blogs})

@login_required(login_url='/accounts/login/')
def my_blogs(request):
    blog_list = BlogPost.objects.filter(author=request.user)

    paginator = Paginator(blog_list, 6)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)

    return render(request, "blogs/my_blogs.html", {"blogs": blogs})

@login_required(login_url='/accounts/login/')
def create(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.content = bleach.clean(
                form.cleaned_data["content"],
                tags=["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"],
                attributes={"a": ["href", "target"], "span": ["class", "contenteditable"]},
            )
            blog_post.save()
            form.save_m2m()

            messages.success(request, "Blog created successfully.")
            return redirect("detail", blog_id=blog_post.pk)
    else:
        form = BlogPostForm()

    return render(request, "blogs/create.html", {"form": form})

@login_required(login_url='/accounts/login/')
def edit(request, blog_id):
    blog = get_object_or_404(BlogPost, pk=blog_id)

    if request.user != blog.author and not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.content = bleach.clean(
                form.cleaned_data["content"],
                tags=["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"],
                attributes={"a": ["href", "target"], "span": ["class", "contenteditable"]},
            )
            blog_post.save()
            form.save_m2m()

            messages.success(request, "Blog updated successfully.")
            return redirect("detail", blog_id=blog_post.pk)
    else:
        form = BlogPostForm(instance=blog)

    return render(request, "blogs/edit.html", {"form": form, "blog": blog})

@login_required(login_url='/accounts/login')
def delete(request, blog_id):
    blog = get_object_or_404(BlogPost, pk=blog_id)
    
    if request.user != blog.author and not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        blog.delete()

        messages.success(request, "Blog deleted successfully.")
        return redirect("my_blogs")
    
    return render(request, "blogs/delete.html", {"blog": blog})