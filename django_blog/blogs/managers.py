from typing import List, Optional
from accounts.models import EmailUser
from django.db import models

class BlogPostQuerySet(models.QuerySet):
    def recent(self, limit: Optional[int] = 3):
        """
        Get most recent blogs.
        """
        return self.order_by("-created_at")[:limit]

    def related_to(self, blog, limit: Optional[int] = 3):
        """
        Get random blogs related by tags.
        """
        return self.filter(tags__in=blog.tags.all()).exclude(pk=blog.pk).distinct().order_by("?")[:limit]

    def by_author(self, user: EmailUser):
        """
        Get blogs by author.
        """
        return self.filter(author=user)

    def search_by_title(self, query: Optional[str]):
        """
        Search blogs by title.
        """
        if query:
            return self.filter(title__icontains=query).distinct()

        return self

    def with_tags(self, tag_slugs: List[str]):
        """
        Filter blogs by tag slugs.
        """
        for tag_slug in tag_slugs:
            self = self.filter(tags__slug=tag_slug).distinct()

        return self

class BlogPostManager(models.Manager):
    def create_blog_post(self, title: str, content: str, image: str, author: EmailUser, tags):
        """
        Creates new blog
        """
        blog_post = self.create(title=title, content=content, image=image, author=author)
        blog_post.tags.set(tags)
        return blog_post

    def update_blog_post(self, blog_post, title: str, content: str, image: str, tags):
        """
        Update an existing blog post.
        """
        blog_post.title = title
        blog_post.content = content
        blog_post.image = image
        blog_post.save()
        blog_post.tags.set(tags)
        return blog_post