import bleach
from blogs.models import BlogPost, Tag
from django.http import Http404
from .forms import BlogPostForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

def index(request):
    blogs = BlogPost.objects.order_by("-created_at")[:3]
    tags = Tag.objects.all()

    print(blogs[0].tags.all())

    return render(request, "blogs/index.html", {"blogs": blogs, "tags": tags})

def blogs(request):
    blogs = BlogPost.objects.all()

    return render(request, "blogs/blogs.html", {"blogs": blogs})

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