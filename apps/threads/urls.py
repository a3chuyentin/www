"""
URL configuration for threads app.
Path: apps/threads/urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ThreadListView.as_view(), name='thread_list'),
    path('<int:pk>/', views.ThreadDetailView.as_view(), name='thread_detail'),
    path('new/', views.thread_create_view, name='thread_create'),
    path('<int:pk>/edit/', views.thread_update_view, name='thread_update'),
    path('<int:pk>/delete/', views.thread_delete_view, name='thread_delete'),
    path('<int:thread_pk>/resolve/', views.resolve_thread_view, name='resolve_thread'),
    path('<int:thread_pk>/comment/', views.thread_comment_view, name='thread_comment'),
    path('comment/<int:comment_pk>/vote/', views.thread_comment_vote_view, name='thread_comment_vote'),
    path('comment/<int:comment_pk>/edit/', views.thread_comment_edit_view, name='thread_comment_edit'),
    path('comment/<int:comment_pk>/delete/', views.thread_comment_delete_view, name='thread_comment_delete'),
    path('hashtag/<slug:slug>/', views.thread_hashtag_view, name='thread_hashtag_view'),
]