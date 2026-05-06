"""
Admin configuration for threads app.
Path: apps/threads/admin.py
"""

from django.contrib import admin
from .models import Thread, ThreadHashtag, ThreadComment, ThreadCommentVote

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['title', 'content', 'author__username']

@admin.register(ThreadHashtag)
class ThreadHashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ThreadComment)
class ThreadCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'thread', 'created_at', 'vote_score', 'parent']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'thread__title']
    
    def vote_score(self, obj):
        return obj.total_votes()
    vote_score.short_description = 'Điểm vote'

@admin.register(ThreadCommentVote)
class ThreadCommentVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'value', 'created_at']
    list_filter = ['value', 'created_at']