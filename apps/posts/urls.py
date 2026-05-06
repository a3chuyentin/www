"""
URL configuration for posts app.
Path: apps/posts/urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.post_create_view, name='post_create'),
    path('post/<int:pk>/edit/', views.post_update_view, name='post_update'),
    path('post/<int:pk>/delete/', views.post_delete_view, name='post_delete'),
    path('hashtag/<slug:slug>/', views.hashtag_view, name='hashtag_view'),
    path('post/<int:post_pk>/comment/', views.post_comment_view, name='post_comment'),
    path('post/<int:post_pk>/vote/', views.post_vote_view, name='post_vote'),
    path('comment/<int:comment_pk>/vote/', views.post_comment_vote_view, name='post_comment_vote'),
    path('comment/<int:comment_pk>/edit/', views.post_comment_edit_view, name='post_comment_edit'),
    path('comment/<int:comment_pk>/delete/', views.post_comment_delete_view, name='post_comment_delete'),
    path('api/load-more/', views.load_more_posts, name='load_more_posts'),
]