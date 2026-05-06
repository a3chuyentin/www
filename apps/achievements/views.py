"""
Views for achievements page.
Path: apps/achievements/views.py
"""

from django.shortcuts import render
from .models import AchievementPage

def achievement_list_view(request):
    """Display achievements page with markdown content from admin."""
    page = AchievementPage.objects.first()
    if not page:
        page = AchievementPage.objects.create(title='Thành tích', content='')
    
    return render(request, 'achievements/achievement_list.html', {'page': page})