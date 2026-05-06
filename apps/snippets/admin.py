"""
Admin configuration for snippets app.
Path: apps/snippets/admin.py
"""

from django.contrib import admin
from .models import Snippet, SnippetVote, SnippetComment, SnippetCommentVote

@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'language', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['title', 'description', 'content', 'author__username']

@admin.register(SnippetComment)
class SnippetCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'snippet', 'created_at', 'vote_score']
    
    def vote_score(self, obj):
        return obj.total_votes()
    vote_score.short_description = 'Điểm vote'

@admin.register(SnippetVote)
class SnippetVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'snippet', 'value', 'created_at']

@admin.register(SnippetCommentVote)
class SnippetCommentVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'value', 'created_at']