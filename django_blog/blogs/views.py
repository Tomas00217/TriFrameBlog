import bleach
from blogs.models import BlogPost, Tag
from django.http import Http404
from .forms import BlogPostForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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
        blog_list = blog_list.filter(tags__slug__in=tag_slugs_list).distinct()

    search = request.GET.get('search')

    if search:
        blog_list = blog_list.filter(title__icontains=search).distinct()

    paginator = Paginator(blog_list, 3)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)

    return render(request, "blogs/blogs.html", {"blogs": blogs, "tags": tags, "selected_tags": tag_slugs_list})

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

            return redirect("blogs")
        print(form)
    else:
        form = BlogPostForm()

    return render(request, "blogs/create.html", {"form": form})

def detail(request, blog_id):
    try:
        blog = BlogPost.objects.get(pk=blog_id)
    except BlogPost.DoesNotExist:
        raise Http404("Blog does not exist")
    return render(request, "blogs/detail.html", {"blog": blog})