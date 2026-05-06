"""
Admin configuration for achievements app.
Path: apps/achievements/admin.py
"""

from django.contrib import admin
from .models import AchievementPage

@admin.register(AchievementPage)
class AchievementPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated_at']
    fields = ['title', 'content']
    widgets = {
        'content': admin.widgets.AdminTextareaWidget(attrs={'rows': 20, 'class': 'markdown-editor'})
    }