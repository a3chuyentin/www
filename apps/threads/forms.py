"""
Forms for threads and comments.
Path: apps/threads/forms.py
"""

from django import forms
from .models import Thread, ThreadHashtag, ThreadComment


class ThreadForm(forms.ModelForm):
    """Form for creating/editing threads with hashtags."""
    hashtag_names = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nhập hashtag cách nhau bằng dấu phẩy (ví dụ: python, django, hỏi đáp)'
        }),
        help_text='Nhập hashtag cách nhau bằng dấu phẩy'
    )
    
    class Meta:
        model = Thread
        fields = ['title', 'content', 'hashtag_names']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nhập tiêu đề câu hỏi...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 10,
                'id': 'markdown-editor',          
                'data-editor': 'true'             
            }),
        }
    
    def save(self, author, commit=True):
        thread = super().save(commit=False)
        thread.author = author
        thread.status = 'APPROVED'
        if commit:
            thread.save()
            hashtag_names = self.cleaned_data.get('hashtag_names', '')
            if hashtag_names:
                hashtags = [name.strip().lower() for name in hashtag_names.split(',') if name.strip()]
                thread.hashtags.clear()
                for hashtag_name in hashtags:
                    hashtag, created = ThreadHashtag.objects.get_or_create(name=hashtag_name)
                    thread.hashtags.add(hashtag)
        return thread


class ThreadCommentForm(forms.ModelForm):
    """Form for thread comments with Markdown."""
    class Meta:
        model = ThreadComment
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