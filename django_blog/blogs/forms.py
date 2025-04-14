from typing import Optional
from accounts.models import EmailUser
from django import forms
from .models import BlogPost, Tag
from html_sanitizer import Sanitizer

class BlogPostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = BlogPost
        fields = ['title', 'tags', 'image', 'content']

    def clean_content(self):
        """
        XSS protection, cleans the content of unwanted tags.
        """
        sanitizer = Sanitizer({
            "tags": ["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"],
            "attributes": {
                "a": ["href", "target", "rel"],
                "span": ["class", "contenteditable"],
                "li": ["data-list"]
            },
            "empty": ["br", "p"],
            "separate": ["li", "p", "br"],
        })

        content = self.cleaned_data.get("content", "")
        return sanitizer.sanitize(content)

    def save(self, author: Optional[EmailUser] = None):
        """
        On save of the form either updates or creates new blog.
        """
        if self.instance.pk:
            return BlogPost.objects.update_blog_post(
                blog_post=self.instance,
                title=self.cleaned_data["title"],
                content=self.clean_content(),
                image=self.cleaned_data.get("image"),
                tags=self.cleaned_data["tags"]
            )

        return BlogPost.objects.create_blog_post(
            title=self.cleaned_data["title"],
            content=self.clean_content(),
            image=self.cleaned_data.get("image"),
            author=author,
            tags=self.cleaned_data["tags"]
        )