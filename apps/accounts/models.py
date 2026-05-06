"""
Profile model extending Django User.
Path: apps/accounts/models.py
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import hashlib
from urllib.parse import urlencode

class Profile(models.Model):
    """User profile model with additional fields."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name='Giới thiệu')
    quote = models.CharField(max_length=200, blank=True, verbose_name='Quote cá nhân')
    full_name = models.CharField(max_length=150, blank=True, verbose_name='Họ tên thật')
    
    def get_gravatar_url(self, size=150):
        """Get Gravatar URL from email without exposing email."""
        email_hash = hashlib.md5(self.user.email.lower().encode()).hexdigest()
        gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}"
        params = urlencode({
            's': str(size),
            'd': 'identicon',
            'r': 'g'
        })
        return f"{gravatar_url}?{params}"
    
    def get_avatar_url(self):
        """Get avatar URL (Gravatar only, no local upload)."""
        return self.get_gravatar_url()
    
    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create Profile when User is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Auto-save Profile when User is saved."""
    instance.profile.save()