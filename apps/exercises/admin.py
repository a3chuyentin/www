"""
Admin configuration for exercises app.
Path: apps/exercises/admin.py
"""

from django.contrib import admin
from .models import Exercise, ExerciseHashtag, ExerciseComment, ExerciseVote, ExerciseCommentVote

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Admin for Exercise model."""
    list_display = ['title', 'author', 'created_at', 'vote_score']
    list_filter = ['created_at']
    search_fields = ['title', 'description', 'author__username']
    
    def vote_score(self, obj):
        return obj.total_votes()
    vote_score.short_description = 'Điểm vote'

@admin.register(ExerciseHashtag)
class ExerciseHashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ExerciseComment)
class ExerciseCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'exercise', 'created_at', 'vote_score']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'exercise__title']
    
    def vote_score(self, obj):
        return obj.total_votes()
    vote_score.short_description = 'Điểm vote'

@admin.register(ExerciseCommentVote)
class ExerciseCommentVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'value', 'created_at']
    list_filter = ['value', 'created_at']

@admin.register(ExerciseVote)
class ExerciseVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'value', 'created_at']
    list_filter = ['value', 'created_at']