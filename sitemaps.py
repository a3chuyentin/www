"""
Sitemap configuration cho A3 Chuyên Tin.
Tự động sinh sitemap.xml cho SEO.
Path: sitemaps.py
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from apps.posts.models import Post, PostHashtag
from apps.threads.models import Thread, ThreadHashtag


class StaticViewSitemap(Sitemap):
    """Sitemap cho các trang tĩnh."""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            'home',
            'about',
            'member',
            'thread_list',
            'exercise_list',
            'achievement_list',
            'snippet_list',
        ]

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    """Sitemap cho bài viết blog."""
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Post.objects.filter(status='APPROVED').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('post_detail', kwargs={'pk': obj.pk})


class HashtagSitemap(Sitemap):
    """Sitemap cho các trang hashtag."""
    changefreq = "weekly"
    priority = 0.4

    def items(self):
        return list(PostHashtag.objects.all())

    def location(self, obj):
        return reverse('hashtag_view', kwargs={'slug': obj.slug})


class ThreadSitemap(Sitemap):
    """Sitemap cho các thread hỏi đáp."""
    changefreq = "daily"
    priority = 0.6

    def items(self):
        from apps.threads.models import Thread
        return Thread.objects.filter(status='APPROVED')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('thread_detail', kwargs={'pk': obj.pk})


class ExerciseSitemap(Sitemap):
    """Sitemap cho các bài tập."""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        from apps.exercises.models import Exercise
        return Exercise.objects.filter(status='APPROVED')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('exercise_detail', kwargs={'pk': obj.pk})


class SnippetSitemap(Sitemap):
    """Sitemap cho code snippets."""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        from apps.snippets.models import Snippet
        return Snippet.objects.filter(status='APPROVED')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('snippet_detail', kwargs={'pk': obj.pk})


class ProfileSitemap(Sitemap):
    """Sitemap cho profile thành viên."""
    changefreq = "monthly"
    priority = 0.3

    def items(self):
        from django.contrib.auth.models import User
        return User.objects.all().order_by('-date_joined')

    def location(self, obj):
        return reverse('profile_detail', kwargs={'username': obj.username})