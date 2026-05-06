"""
Page models for static pages with markdown content.
Path: apps/pages/models.py
"""

from django.db import models

class AboutPage(models.Model):
    """About page model with markdown content."""
    title = models.CharField(max_length=200, default='Về chúng mình')
    content = models.TextField(blank=True, help_text='Nội dung Markdown cho trang giới thiệu')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Trang giới thiệu'
        verbose_name_plural = 'Trang giới thiệu'


class MemberPage(models.Model):
    """Member page model with markdown content."""
    title = models.CharField(max_length=200, default='Thành viên')
    content = models.TextField(blank=True, help_text='Nội dung Markdown cho trang thành viên')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Trang thành viên'
        verbose_name_plural = 'Trang thành viên'