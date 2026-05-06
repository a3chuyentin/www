"""
Gravatar utility functions.
Path: apps/accounts/utils.py
"""

import hashlib
from urllib.parse import urlencode

def get_gravatar_url(email, size=150):
    """Get Gravatar URL from email."""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    params = urlencode({
        's': str(size),
        'd': 'identicon',
        'r': 'g'
    })
    return f"https://www.gravatar.com/avatar/{email_hash}?{params}"