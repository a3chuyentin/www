"""
Views for static pages.
Path: apps/pages/views.py
"""

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q
from .models import AboutPage


def about_view(request):
    """Display about page with markdown content from admin."""
    page = AboutPage.objects.first()
    if not page:
        page = AboutPage.objects.create(title='Về chúng mình', content='')
    
    return render(request, 'pages/about.html', {'page': page})


def member_view(request):
    """Display member page with user statistics."""
    members = User.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='APPROVED'), distinct=True),
        thread_count=Count('threads', distinct=True),
        exercise_count=Count('exercises', distinct=True),
        snippet_count=Count('snippets', distinct=True)
    ).order_by('-post_count', '-thread_count', '-exercise_count')
    
    return render(request, 'pages/member.html', {'members': members})