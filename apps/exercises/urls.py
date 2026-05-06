"""
URL configuration for exercises app.
Path: apps/exercises/urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.exercise_list_view, name='exercise_list'),
    path('<int:pk>/', views.exercise_detail_view, name='exercise_detail'),
    path('new/', views.exercise_create_view, name='exercise_create'),
    path('<int:pk>/edit/', views.exercise_update_view, name='exercise_update'),
    path('<int:pk>/delete/', views.exercise_delete_view, name='exercise_delete'),
    path('<int:exercise_pk>/comment/', views.exercise_comment_view, name='exercise_comment'),
    path('<int:exercise_pk>/vote/', views.exercise_vote_view, name='exercise_vote'),
    path('comment/<int:comment_pk>/vote/', views.exercise_comment_vote_view, name='exercise_comment_vote'),
    path('comment/<int:comment_pk>/edit/', views.exercise_comment_edit_view, name='exercise_comment_edit'),
    path('comment/<int:comment_pk>/delete/', views.exercise_comment_delete_view, name='exercise_comment_delete'),
    path('hashtag/<slug:slug>/', views.exercise_hashtag_view, name='exercise_hashtag_view'),
]