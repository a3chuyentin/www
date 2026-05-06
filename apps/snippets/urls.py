"""
URL configuration for snippets app.
Path: apps/snippets/urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.snippet_list_view, name='snippet_list'),
    path('<int:pk>/', views.snippet_detail_view, name='snippet_detail'),
    path('new/', views.snippet_create_view, name='snippet_create'),
    path('<int:pk>/edit/', views.snippet_update_view, name='snippet_update'),
    path('<int:pk>/delete/', views.snippet_delete_view, name='snippet_delete'),
    path('<int:snippet_pk>/comment/', views.snippet_comment_view, name='snippet_comment'),
    path('<int:snippet_pk>/vote/', views.snippet_vote_view, name='snippet_vote'),
    path('comment/<int:comment_pk>/vote/', views.snippet_comment_vote_view, name='snippet_comment_vote'),
    path('comment/<int:comment_pk>/edit/', views.snippet_comment_edit_view, name='snippet_comment_edit'),
    path('comment/<int:comment_pk>/delete/', views.snippet_comment_delete_view, name='snippet_comment_delete'),
]