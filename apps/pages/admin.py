"""
Admin configuration for pages app.
Path: apps/pages/admin.py
"""

from django.contrib import admin
from .models import AboutPage, MemberPage

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated_at']
    fields = ['title', 'content']
    widgets = {
        'content': admin.widgets.AdminTextareaWidget(attrs={'rows': 20, 'class': 'markdown-editor'})
    }

@admin.register(MemberPage)
class MemberPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated_at']
    fields = ['title', 'content']
    widgets = {
        'content': admin.widgets.AdminTextareaWidget(attrs={'rows': 20, 'class': 'markdown-editor'})
    }