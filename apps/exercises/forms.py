"""
Forms for exercises and comments.
Path: apps/exercises/forms.py
"""

from django import forms
from .models import Exercise, ExerciseHashtag, ExerciseComment

class ExerciseForm(forms.ModelForm):
    """Form for creating/editing exercises with hashtags."""
    hashtag_names = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nhập hashtag cách nhau bằng dấu phẩy (ví dụ: baitap, python, dsa)'
        }),
        help_text='Nhập hashtag cách nhau bằng dấu phẩy'
    )
    
    class Meta:
        model = Exercise
        fields = ['title', 'description', 'url', 'solution', 'hashtag_names']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nhập tiêu đề bài tập...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 5, 
                'placeholder': 'Mô tả bài tập...', 
                'data-editor': 'true'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-input', 
                'placeholder': 'https://...'
            }),
            'solution': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 5, 
                'placeholder': 'Lời giải (sẽ ẩn/hiện)', 
                'data-editor': 'true'
            }),
        }
    
    def clean_description(self):
        """Sanitize markdown description."""
        from apps.utils.sanitizer import sanitize_markdown
        return sanitize_markdown(self.cleaned_data.get('description', ''))
    
    def clean_solution(self):
        """Sanitize markdown solution."""
        from apps.utils.sanitizer import sanitize_markdown
        return sanitize_markdown(self.cleaned_data.get('solution', ''))
    
    def save(self, author, commit=True):
        """Save exercise with hashtags. Auto-approved."""
        exercise = super().save(commit=False)
        exercise.author = author
        exercise.status = 'APPROVED'  # Auto-approve
        if commit:
            exercise.save()
            hashtag_names = self.cleaned_data.get('hashtag_names', '')
            if hashtag_names:
                hashtags = [name.strip().lower() for name in hashtag_names.split(',') if name.strip()]
                exercise.hashtags.clear()
                for hashtag_name in hashtags:
                    hashtag, created = ExerciseHashtag.objects.get_or_create(name=hashtag_name)
                    exercise.hashtags.add(hashtag)
        return exercise


class ExerciseCommentForm(forms.ModelForm):
    """Form for exercise comments with Markdown."""
    class Meta:
        model = ExerciseComment
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