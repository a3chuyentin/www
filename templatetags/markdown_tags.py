"""
Markdown rendering template tags with XSS protection.
Path: templatetags/markdown_tags.py
"""

from django import template
from django.utils.safestring import mark_safe
import markdown
from apps.utils.sanitizer import sanitize_html

register = template.Library()

@register.filter
def render_markdown(content):
    """
    Render markdown to HTML with XSS protection.
    Usage: {{ post.content|render_markdown }}
    """
    if not content:
        return ''
    
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
        ]
    )
    
    html = md.convert(content)
    
    safe_html = sanitize_html(html)
    
    return mark_safe(safe_html)

@register.filter
def truncate_markdown(content, length=200):
    """Truncate markdown content for preview."""
    if not content:
        return ''
    
    import re
    plain_text = re.sub(r'[#*_`>\[\]()!]', '', content)
    if len(plain_text) > length:
        plain_text = plain_text[:length] + '...'
    
    return plain_text