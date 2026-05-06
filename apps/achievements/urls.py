"""
URL configuration for achievements app.
Path: apps/achievements/urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.achievement_list_view, name='achievement_list'),
]