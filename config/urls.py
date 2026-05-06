"""
Root URL configuration for A3 Chuyen Tin project.
Path: config/urls.py
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.posts import views as posts_views

from sitemaps import (
    PostSitemap, ThreadSitemap, ExerciseSitemap,
    SnippetSitemap, HashtagSitemap, ProfileSitemap, StaticViewSitemap
)

sitemaps = {
    'static': StaticViewSitemap,
    'posts': PostSitemap,
    'hashtags': HashtagSitemap,
    'threads': ThreadSitemap,
    'exercises': ExerciseSitemap,
    'snippets': SnippetSitemap,
    'profiles': ProfileSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', posts_views.PostListView.as_view(), name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('posts/', include('apps.posts.urls')),
    path('exercises/', include('apps.exercises.urls')),
    path('threads/', include('apps.threads.urls')),
    path('achievements/', include('apps.achievements.urls')),
    path('pages/', include('apps.pages.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('snippets/', include('apps.snippets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)