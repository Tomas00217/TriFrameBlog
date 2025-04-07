from typing import Optional
from accounts.models import EmailUser
import bleach
from django import forms
from .models import BlogPost, Tag

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
        allowed_tags = ["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"]
        allowed_attrs = {"a": ["href", "target"], "span": ["class", "contenteditable"]}

        content = self.cleaned_data.get("content", "")
        return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)

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