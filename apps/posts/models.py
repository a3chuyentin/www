"""
Post and Hashtag models for blog system.
Path: apps/posts/models.py
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class PostHashtag(models.Model):
    """Hashtag model for categorizing posts."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"#{self.name}"

class Post(models.Model):
    """Blog post model with Markdown content."""
    
    POST_TYPE_CHOICES = [
        ('ACADEMIC', 'Học thuật'),
        ('CASUAL', 'Góc vui'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Chờ duyệt'),
        ('APPROVED', 'Đã duyệt'),
        ('REJECTED', 'Từ chối'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='CASUAL')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    hashtags = models.ManyToManyField(PostHashtag, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
    
    def increment_views(self):
        """Increment view count for this post."""
        self.views += 1
        self.save(update_fields=['views'])
    
    def total_votes(self):
        """Get total votes (up - down)."""
        return self.votes.aggregate(total=models.Sum('value'))['total'] or 0

class PostComment(models.Model):
    """Nested comment on blog posts."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    def get_depth(self):
        """Get comment depth level (0 for root)."""
        depth = 0
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth
    
    def total_votes(self):
        """Get total votes for this comment."""
        return self.votes.aggregate(total=models.Sum('value'))['total'] or 0

class PostCommentVote(models.Model):
    """Vote on post comments (up=1, down=-1)."""
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_comment_votes')
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} voted {self.value} on comment {self.comment.id}"

class PostVote(models.Model):
    """Vote on blog posts (up=1, down=-1)."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_votes')
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.username} voted {self.value} on {self.post.title}"
    
class PostRevision(models.Model):
    """
    Lưu bản nháp chỉnh sửa của bài viết.
    Khi admin duyệt, nội dung sẽ được áp dụng vào bài gốc.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='revisions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=Post.POST_TYPE_CHOICES)
    hashtags = models.ManyToManyField(PostHashtag, related_name='revisions')
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Revision for {self.post.title} by {self.edited_by.username}"

    def apply_revision(self):
        """Apply this revision to the original post."""
        self.post.title = self.title
        self.post.content = self.content
        self.post.post_type = self.post_type
        self.post.save()
        self.post.hashtags.set(self.hashtags.all())
        self.is_approved = True
        self.save()