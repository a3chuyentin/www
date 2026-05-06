"""
URL configuration for pages app.
Path: apps/pages/urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about_view, name='about'),
    path('member/', views.member_view, name='member'),
]