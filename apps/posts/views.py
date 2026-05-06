"""
Views for blog post CRUD operations and listing.
Path: apps/posts/views.py
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.db import models
from django.db.models import Sum, Value, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import random
from .models import Post, PostHashtag, PostComment, PostVote, PostCommentVote, PostRevision
from .forms import PostForm, CommentForm


def get_ranked_posts(queryset, limit=10, offset=0):
    """
    Get posts ranked by: likes > views > newest.
    """
    ranked_posts = list(queryset.annotate(
        like_count=Coalesce(Sum('votes__value'), Value(0), output_field=IntegerField())
    ).order_by('-like_count', '-views', '-created_at'))
    
    total_posts = len(ranked_posts)
    
    if total_posts == 0:
        return [], 0
    
    if offset >= total_posts:
        offset = offset % total_posts
    
    result_posts = []
    for i in range(limit):
        idx = (offset + i) % total_posts
        result_posts.append(ranked_posts[idx])
    
    return result_posts, total_posts


class PostListView(ListView):
    """Home page feed with ranking algorithm."""
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='APPROVED')
        
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(content__icontains=search_query) |
                models.Q(author__username__icontains=search_query)
            )
        
        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'academic':
            queryset = queryset.filter(post_type='ACADEMIC')
        elif filter_type == 'casual':
            queryset = queryset.filter(post_type='CASUAL')
        
        posts, total = get_ranked_posts(queryset, limit=self.paginate_by, offset=0)
        self.total_posts = total
        
        if self.request.user.is_authenticated:
            for post in posts:
                try:
                    post.user_vote = PostVote.objects.get(post=post, user=self.request.user).value
                except PostVote.DoesNotExist:
                    post.user_vote = 0
        else:
            for post in posts:
                post.user_vote = 0
        
        return posts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_type'] = self.request.GET.get('filter', 'all')
        context['search_query'] = self.request.GET.get('q', '')
        context['search_action'] = '/'
        context['total_posts'] = self.total_posts
        
        from django.core.paginator import Paginator, Page
        paginator = Paginator(range(self.total_posts), self.paginate_by)
        page_number = 1
        context['page_obj'] = Page(list(range(len(self.object_list))), page_number, paginator)
        context['is_paginated'] = self.total_posts > self.paginate_by
        
        week_ago = timezone.now() - timedelta(days=7)
        context['hot_posts'] = Post.objects.filter(
            status='APPROVED', created_at__gte=week_ago
        ).order_by('-views')[:5]
        
        return context


def load_more_posts(request):
    """API endpoint for infinite scroll."""
    page = int(request.GET.get('page', 1))
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('q', '')
    
    page_size = 5
    offset = (page - 1) * page_size
    
    queryset = Post.objects.filter(status='APPROVED')
    
    if search_query:
        queryset = queryset.filter(
            models.Q(title__icontains=search_query) |
            models.Q(content__icontains=search_query) |
            models.Q(author__username__icontains=search_query)
        )
    
    if filter_type == 'academic':
        queryset = queryset.filter(post_type='ACADEMIC')
    elif filter_type == 'casual':
        queryset = queryset.filter(post_type='CASUAL')
    
    total_posts = queryset.count()
    
    if total_posts == 0:
        return JsonResponse({
            'html': '',
            'has_next': False,
            'page': page,
            'count': 0
        })
    
    posts, total_ranked = get_ranked_posts(queryset, limit=page_size, offset=offset % max(total_posts, 1))
    
    if len(posts) == 0 and total_posts > 0:
        offset = 0
        posts, total_ranked = get_ranked_posts(queryset, limit=page_size, offset=offset)
    
    from django.template.loader import render_to_string
    html = ''
    for post in posts:
        if request.user.is_authenticated:
            try:
                post.user_vote = PostVote.objects.get(post=post, user=request.user).value
            except PostVote.DoesNotExist:
                post.user_vote = 0
        else:
            post.user_vote = 0
        html += render_to_string('posts/post_card.html', {'post': post, 'request': request})
    
    has_next = True
    
    return JsonResponse({
        'html': html,
        'has_next': has_next,
        'page': page + 1 if len(posts) > 0 else 2,
        'count': len(posts)
    })


class PostDetailView(DetailView):
    """Display single post with nested comments."""
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(status='APPROVED')
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increment_views()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        
        all_comments = self.object.comments.all().order_by('created_at')
        
        def build_comment_tree(comments):
            comment_dict = {}
            for comment in comments:
                comment_dict[comment.id] = comment
                comment.children = []
            
            roots = []
            for comment in comments:
                if comment.parent_id and comment.parent_id in comment_dict:
                    comment_dict[comment.parent_id].children.append(comment)
                else:
                    roots.append(comment)
            
            roots.sort(key=lambda x: x.created_at, reverse=True)
            return roots
        
        comment_tree = build_comment_tree(list(all_comments))
        
        if self.request.user.is_authenticated:
            def add_user_votes(comments):
                for comment in comments:
                    try:
                        comment.user_vote = PostCommentVote.objects.get(
                            comment=comment, user=self.request.user
                        ).value
                    except PostCommentVote.DoesNotExist:
                        comment.user_vote = 0
                    if hasattr(comment, 'children') and comment.children:
                        add_user_votes(comment.children)
            
            add_user_votes(comment_tree)
        else:
            def add_user_votes_zero(comments):
                for comment in comments:
                    comment.user_vote = 0
                    if hasattr(comment, 'children') and comment.children:
                        add_user_votes_zero(comment.children)
            
            add_user_votes_zero(comment_tree)
        
        context['comment_tree'] = comment_tree
        
        if self.request.user.is_authenticated:
            try:
                context['user_vote'] = PostVote.objects.get(
                    post=self.object, user=self.request.user
                ).value
            except PostVote.DoesNotExist:
                context['user_vote'] = 0
        else:
            context['user_vote'] = 0
        
        return context


@login_required
def post_create_view(request):
    """Create new blog post."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(author=request.user)
            messages.success(request, 'Bài viết đã được gửi và chờ admin duyệt!')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form, 'title': 'Tạo bài viết mới'})


@login_required
def post_update_view(request, pk):
    """Update existing blog post (author only). Creates revision pending approval."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'Bạn không có quyền sửa bài viết này.')
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            revision = PostRevision.objects.create(
                post=post,
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                post_type=form.cleaned_data['post_type'],
                edited_by=request.user
            )

            hashtag_names = form.cleaned_data['hashtag_names']
            hashtags = [name.strip().lower() for name in hashtag_names.split(',') if name.strip()]
            for hashtag_name in hashtags:
                hashtag, created = PostHashtag.objects.get_or_create(name=hashtag_name)
                revision.hashtags.add(hashtag)

            messages.success(request, 'Bản chỉnh sửa đã được gửi và chờ admin duyệt! Bài viết gốc vẫn hiển thị.')
            return redirect('post_detail', pk=post.pk)
    else:
        initial_hashtags = ', '.join([h.name for h in post.hashtags.all()])
        form = PostForm(instance=post, initial={'hashtag_names': initial_hashtags})
    return render(request, 'posts/post_form.html', {'form': form, 'title': 'Chỉnh sửa bài viết'})


@login_required
def post_delete_view(request, pk):
    """Delete blog post (author only)."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'Bạn không có quyền xóa bài viết này.')
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Bài viết đã được xóa!')
        return redirect('home')
    return render(request, 'posts/post_confirm_delete.html', {'post': post})


def hashtag_view(request, slug):
    """View posts filtered by hashtag."""
    hashtag = get_object_or_404(PostHashtag, slug=slug)
    posts = hashtag.posts.filter(status='APPROVED').order_by('-created_at')
    return render(request, 'posts/hashtag_posts.html', {
        'hashtag': hashtag,
        'posts': posts,
    })


@login_required
def post_comment_view(request, post_pk):
    """Add nested comment to post."""
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Đã thêm bình luận!')
    return redirect('post_detail', pk=post_pk)


@login_required
def post_comment_edit_view(request, comment_pk):
    """Edit own comment."""
    comment = get_object_or_404(PostComment, pk=comment_pk)
    
    if comment.author != request.user:
        return JsonResponse({'error': 'Bạn không có quyền sửa bình luận này.'}, status=403)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        if content.strip():
            comment.content = content
            comment.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Nội dung không được để trống.'}, status=400)


@login_required
def post_comment_delete_view(request, comment_pk):
    """
    Delete comment.
    Author can delete own comment. Post owner can delete any comment on their post.
    """
    comment = get_object_or_404(PostComment, pk=comment_pk)
    post = comment.post
    
    if comment.author != request.user and post.author != request.user:
        return JsonResponse({'error': 'Bạn không có quyền xóa bình luận này.'}, status=403)
    
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def post_comment_vote_view(request, comment_pk):
    """Vote on post comment (up=1, down=-1)."""
    comment = get_object_or_404(PostComment, pk=comment_pk)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    value = int(request.POST.get('value', 0))
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote value'}, status=400)
    
    vote, created = PostCommentVote.objects.get_or_create(
        comment=comment,
        user=request.user,
        defaults={'value': value}
    )
    
    if not created:
        if vote.value == value:
            vote.delete()
            value = 0
        else:
            vote.value = value
            vote.save()
    
    return JsonResponse({
        'total_votes': comment.total_votes(),
        'user_vote': value if value != 0 else 0
    })


@login_required
def post_vote_view(request, post_pk):
    """Vote on post (up=1, down=-1)."""
    post = get_object_or_404(Post, pk=post_pk)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    value = int(request.POST.get('value', 0))
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote value'}, status=400)
    
    vote, created = PostVote.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={'value': value}
    )
    
    if not created:
        if vote.value == value:
            vote.delete()
            value = 0
        else:
            vote.value = value
            vote.save()
    
    return JsonResponse({
        'total_votes': post.total_votes(),
        'user_vote': value if value != 0 else 0
    })