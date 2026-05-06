"""
Forms for user authentication and profile management.
Path: apps/accounts/forms.py
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    """User registration form with additional fields."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    full_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.profile.full_name = self.cleaned_data['full_name']
            user.profile.save()
        return user

class UserUpdateForm(forms.ModelForm):
    """Form to update user basic info (username and email are locked)."""
    
    class Meta:
        model = User
        fields = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username_display'] = forms.CharField(
            label='Tên đăng nhập',
            initial=self.instance.username,
            disabled=True,
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
        )
        self.fields['email_display'] = forms.EmailField(
            label='Email',
            initial=self.instance.email,
            disabled=True,
            required=False,
            widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
        )

class ProfileUpdateForm(forms.ModelForm):
    """Form to update profile info (without avatar)."""
    class Meta:
        model = Profile
        fields = ['full_name', 'bio', 'quote']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'quote': forms.TextInput(attrs={'class': 'form-control'}),
        }