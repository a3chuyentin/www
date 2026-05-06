"""
Views for user authentication and profile management.
Path: apps/accounts/views.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import DetailView
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from apps.posts.models import Post

def register_view(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Chào mừng {user.username} trở lại!')
            return redirect('home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('home')

@login_required
def profile_view(request):
    """View and edit current user's profile."""
    if request.method == 'POST':
        profile = request.user.profile
        profile.full_name = request.POST.get('full_name', '')
        profile.bio = request.POST.get('bio', '')
        profile.quote = request.POST.get('quote', '')
        profile.save()
        messages.success(request, 'Cập nhật profile thành công!')
        return redirect('profile')
    
    # GET request
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    
    user_posts = Post.objects.filter(author=request.user, status='APPROVED').order_by('-created_at')[:5]
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_posts': user_posts,
    }
    return render(request, 'accounts/profile.html', context)

class ProfileDetailView(DetailView):
    """View other user's profile by username."""
    model = User
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_posts'] = Post.objects.filter(
            author=self.object, 
            status='APPROVED'
        ).order_by('-created_at')
        return context