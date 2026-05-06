"""
Admin configuration for posts app.
Path: apps/posts/admin.py
"""

from django.contrib import admin
from .models import Post, PostHashtag, PostComment, PostVote, PostCommentVote, PostRevision


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for Post model."""
    list_display = ['title', 'author', 'post_type', 'status', 'created_at']
    list_filter = ['status', 'post_type', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    actions = ['approve_posts', 'reject_posts']

    def approve_posts(self, request, queryset):
        queryset.update(status='APPROVED')
        self.message_user(request, f'Đã duyệt {queryset.count()} bài viết.')
    approve_posts.short_description = 'Duyệt bài viết được chọn'

    def reject_posts(self, request, queryset):
        queryset.update(status='REJECTED')
        self.message_user(request, f'Đã từ chối {queryset.count()} bài viết.')
    reject_posts.short_description = 'Từ chối bài viết được chọn'


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'vote_score']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'post__title']

    def vote_score(self, obj):
        return obj.total_votes()
    vote_score.short_description = 'Điểm vote'


@admin.register(PostCommentVote)
class PostCommentVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'value', 'created_at']
    list_filter = ['value', 'created_at']


@admin.register(PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'value', 'created_at']
    list_filter = ['value', 'created_at']


@admin.register(PostRevision)
class PostRevisionAdmin(admin.ModelAdmin):
    """Admin for PostRevision model."""
    list_display = ['post', 'edited_by', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['post__title', 'edited_by__username', 'title']
    actions = ['approve_revisions']

    def approve_revisions(self, request, queryset):
        for revision in queryset.filter(is_approved=False):
            revision.apply_revision()
        self.message_user(request, f'Đã duyệt {queryset.count()} bản chỉnh sửa.')
    approve_revisions.short_description = 'Duyệt bản chỉnh sửa được chọn'