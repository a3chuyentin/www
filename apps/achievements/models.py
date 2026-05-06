"""
Achievements model for markdown content.
Path: apps/achievements/models.py
"""

from django.db import models

class AchievementPage(models.Model):
    """Single page model for achievements markdown content."""
    title = models.CharField(max_length=200, default='Thành tích')
    content = models.TextField(blank=True, help_text='Nội dung Markdown cho trang thành tích')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Trang thành tích'
        verbose_name_plural = 'Trang thành tích'