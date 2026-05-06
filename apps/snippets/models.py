"""
Snippet model cho code sharing.
Path: apps/snippets/models.py
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Snippet(models.Model):
    """Code snippet sharing model."""
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('csharp', 'C#'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('sql', 'SQL'),
        ('bash', 'Bash'),
        ('rust', 'Rust'),
        ('go', 'Go'),
        ('other', 'Khác'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Chờ duyệt'),
        ('APPROVED', 'Đã duyệt'),
        ('REJECTED', 'Từ chối'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    description = models.TextField(blank=True, verbose_name='Mô tả ngắn')
    content = models.TextField(verbose_name='Nội dung code')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    views = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Snippet: {self.title}"
    
    def get_absolute_url(self):
        return reverse('snippet_detail', kwargs={'pk': self.pk})
    
    def total_votes(self):
        """Get total votes (up - down)."""
        return self.votes.aggregate(total=models.Sum('value'))['total'] or 0


class SnippetVote(models.Model):
    """Vote on snippets (up=1, down=-1)."""
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_votes')
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['snippet', 'user']
    
    def __str__(self):
        return f"{self.user.username} voted {self.value} on {self.snippet.title}"


class SnippetComment(models.Model):
    """Nested comment on snippets."""
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.snippet.title}"
    
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


class SnippetCommentVote(models.Model):
    """Vote on snippet comments (up=1, down=-1)."""
    comment = models.ForeignKey(SnippetComment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_comment_votes')
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} voted {self.value} on comment {self.comment.id}"