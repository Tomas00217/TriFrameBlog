from accounts.models import EmailUser
from blogs.managers import BlogPostManager, BlogPostQuerySet
from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.utils.text import slugify

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = CloudinaryField("image", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, related_name="blog_posts")
    author = models.ForeignKey(EmailUser, on_delete=models.CASCADE)

    objects = BlogPostManager.from_queryset(BlogPostQuerySet)()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title