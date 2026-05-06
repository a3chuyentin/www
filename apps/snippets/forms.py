"""
Forms for snippets and comments.
Path: apps/snippets/forms.py
"""

from django import forms
from .models import Snippet, SnippetComment


class SnippetForm(forms.ModelForm):
    """Form for creating/editing snippets."""
    
    class Meta:
        model = Snippet
        fields = ['title', 'description', 'content', 'language']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tiêu đề snippet...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Mô tả ngắn về code này...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input font-mono',
                'rows': 12,
                'placeholder': 'Code của bạn ở đây...',
                'spellcheck': 'false'
            }),
            'language': forms.Select(attrs={
                'class': 'form-input'
            }),
        }
    
    def save(self, author, commit=True):
        snippet = super().save(commit=False)
        snippet.author = author
        snippet.status = 'APPROVED'  # Auto-approve
        if commit:
            snippet.save()
        return snippet


class SnippetCommentForm(forms.ModelForm):
    """Form for snippet comments with Markdown."""
    class Meta:
        model = SnippetComment
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