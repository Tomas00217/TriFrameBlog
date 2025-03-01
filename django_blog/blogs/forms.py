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