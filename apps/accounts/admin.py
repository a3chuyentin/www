"""
Admin configuration for accounts app.
Path: apps/accounts/admin.py
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    """Inline profile editing trong User admin."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['full_name', 'bio', 'quote', 'avatar']


class CustomUserAdmin(UserAdmin):
    """Custom User admin với profile inline và đầy đủ fields."""
    inlines = (ProfileInline,)
    
    # Thêm các field từ Profile vào list display
    list_display = ('username', 'email', 'full_name', 'is_staff', 'is_active', 'date_joined')
    
    # Thêm field vào form edit
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('first_name', 'last_name', 'email')}),
        ('Quyền hạn', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Ngày quan trọng', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Thêm field vào form tạo mới
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    search_fields = ('username', 'email', 'profile__full_name')
    ordering = ('-date_joined',)
    
    def full_name(self, obj):
        """Hiển thị họ tên thật từ Profile."""
        return obj.profile.full_name or '-'
    full_name.short_description = 'Họ tên thật'
    full_name.admin_order_field = 'profile__full_name'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin riêng cho Profile model."""
    list_display = ['user', 'full_name', 'bio_preview', 'quote']
    search_fields = ['user__username', 'full_name']
    list_filter = ['user__is_active']
    fields = ['user', 'full_name', 'bio', 'quote', 'avatar']
    readonly_fields = ['user']
    
    def bio_preview(self, obj):
        """Preview ngắn cho bio."""
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else obj.bio or '-'
    bio_preview.short_description = 'Giới thiệu'