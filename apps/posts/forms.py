"""
Forms for creating and editing blog posts.
Path: apps/posts/forms.py
"""

from django import forms
from .models import Post, PostHashtag, PostComment

class PostForm(forms.ModelForm):
    """Form for creating/editing blog posts."""
    hashtag_names = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Nhập hashtag cách nhau bằng dấu phẩy (ví dụ: python, django, học tập)'
        }),
        help_text='Nhập hashtag cách nhau bằng dấu phẩy'
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'post_type', 'hashtag_names']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 
                'required': True,
                'placeholder': 'Nhập tiêu đề bài viết...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input', 
                'id': 'markdown-editor', 
                'data-editor': 'true',
                'rows': 15
            }),
            'post_type': forms.Select(attrs={
                'class': 'form-input'
            }),
        }
    
    def clean_content(self):
        """Sanitize markdown content."""
        from apps.utils.sanitizer import sanitize_markdown
        content = self.cleaned_data.get('content', '')
        if not content:
            raise forms.ValidationError('Nội dung không được để trống.')
        return sanitize_markdown(content)
    
    def save(self, author, commit=True):
        post = super().save(commit=False)
        post.author = author
        if commit:
            post.save()
            hashtag_names = self.cleaned_data['hashtag_names']
            hashtags = [name.strip().lower() for name in hashtag_names.split(',') if name.strip()]
            post.hashtags.clear()
            for hashtag_name in hashtags:
                hashtag, created = PostHashtag.objects.get_or_create(name=hashtag_name)
                post.hashtags.add(hashtag)
        return post


class CommentForm(forms.ModelForm):
    """Form for adding comments with Markdown."""
    class Meta:
        model = PostComment
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 3, 
                'placeholder': 'Viết bình luận của bạn...', 
                'data-editor': 'true'
            }),
            'parent': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].required = False
        self.fields['content'].required = False
    
    def clean_content(self):
        """Sanitize comment content."""
        from apps.utils.sanitizer import sanitize_markdown
        content = self.cleaned_data.get('content', '')
        if not content:
            raise forms.ValidationError('Nội dung bình luận không được để trống.')
        return sanitize_markdown(content)