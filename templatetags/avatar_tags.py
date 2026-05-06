"""
Template tags for displaying user avatars.
Path: apps/posts/templatetags/avatar_tags.py
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def user_avatar(user, size=32):
    """
    Get avatar HTML for a user.
    Usage: {{ user|user_avatar }} or {{ user|user_avatar:64 }}
    """
    if not user or not user.is_authenticated:
        return ''
    
    avatar_url = user.profile.get_avatar_url()
    username = user.username
    
    return mark_safe(
        f'<img src="{avatar_url}" alt="{username}" class="avatar-sm" '
        f'style="width: {size}px; height: {size}px; border-radius: 50%; object-fit: cover;">'
    )

@register.simple_tag
def user_avatar_tag(user, size=32):
    """Simple tag to get avatar HTML."""
    if not user or not user.is_authenticated:
        return ''
    
    avatar_url = user.profile.get_avatar_url()
    username = user.username
    
    return mark_safe(
        f'<img src="{avatar_url}" alt="{username}" class="avatar-sm" '
        f'style="width: {size}px; height: {size}px; border-radius: 50%; object-fit: cover;">'
    )