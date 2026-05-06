"""
HTML sanitizer for user-generated content.
Path: apps/utils/sanitizer.py
"""

import bleach
from bleach.css_sanitizer import CSSSanitizer

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'del', 'ins', 'mark',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'code', 'pre', 'blockquote',
    'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span', 'hr', 'details', 'summary'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class'],
    'span': ['class'],
    'table': ['class'],
    'td': ['class'],
    'th': ['class'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']

css_sanitizer = CSSSanitizer(
    allowed_css_properties=[
        'color', 'background-color', 'font-size', 'font-weight',
        'text-align', 'margin', 'padding', 'border'
    ]
)

def sanitize_html(content):
    """
    Sanitize HTML content to prevent XSS attacks.
    Removes script tags, event handlers, and other dangerous content.
    """
    if not content:
        return ''
    
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        css_sanitizer=css_sanitizer,
        strip=True,
        strip_comments=True
    )

def sanitize_markdown(markdown_content):
    """
    Basic sanitization for markdown content before processing.
    Removes any script-like patterns.
    """
    if not markdown_content:
        return ''
    
    import re
    markdown_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', markdown_content, flags=re.IGNORECASE)
    markdown_content = re.sub(r'javascript\s*:', '', markdown_content, flags=re.IGNORECASE)
    markdown_content = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', markdown_content, flags=re.IGNORECASE)
    
    return markdown_content