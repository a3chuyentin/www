"""
Custom template tags for SEO meta generation.
Path: templatetags/seo_tags.py
"""

from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag(takes_context=True)
def seo_meta(context):
    """Generate SEO meta tags for the current page."""
    request = context.get('request')
    post = context.get('post')
    title = context.get('title')
    
    if post:
        return render_to_string('components/seo_meta.html', {'post': post}, request=request)
    elif title:
        return render_to_string('components/seo_meta.html', {'title': title}, request=request)
    else:
        return render_to_string('components/seo_meta.html', request=request)