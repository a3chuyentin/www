"""
Exercise model with solution visibility.
Path: apps/exercises/models.py
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class ExerciseHashtag(models.Model):
    """Hashtag model for exercises."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"#{self.name}"

class Exercise(models.Model):
    """Exercise model with solution."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Chờ duyệt'),
        ('APPROVED', 'Đã duyệt'),
        ('REJECTED', 'Từ chối'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(help_text='Mô tả bài tập')
    url = models.URLField(blank=True, help_text='Link bài tập (nếu có)')
    solution = models.TextField(blank=True, help_text='Lời giải (ẩn/hiện bằng details)')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises')
    hashtags = models.ManyToManyField(ExerciseHashtag, related_name='exercises', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return self.title
    
    def total_votes(self):
        """Get total votes (up - down)."""
        return self.votes.aggregate(total=models.Sum('value'))['total'] or 0

class ExerciseComment(models.Model):
    """Nested comment on exercises."""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.exercise.title}"
    
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

class ExerciseCommentVote(models.Model):
    """Vote on exercise comments (up=1, down=-1)."""
    comment = models.ForeignKey(ExerciseComment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_comment_votes')
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} voted {self.value} on comment {self.comment.id}"

class ExerciseVote(models.Model):
    """Vote on exercises (up=1, down=-1)."""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_votes')
    value = models.SmallIntegerField(choices=[(1, 'Up'), (-1, 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['exercise', 'user']
    
    def __str__(self):
        return f"{self.user.username} voted {self.value} on {self.exercise.title}"