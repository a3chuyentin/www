"""
Views for threads and comments management.
Path: apps/threads/views.py
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.db import models
from django.http import JsonResponse
from .models import Thread, ThreadHashtag, ThreadComment, ThreadCommentVote
from .forms import ThreadForm, ThreadCommentForm


class ThreadListView(ListView):
    """List all question threads with search."""
    model = Thread
    template_name = 'threads/thread_list.html'
    context_object_name = 'threads'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Thread.objects.all()
        
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(content__icontains=search_query) |
                models.Q(author__username__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['search_action'] = '/threads/'
        return context


class ThreadDetailView(DetailView):
    """Display thread with nested comments."""
    model = Thread
    template_name = 'threads/thread_detail.html'
    context_object_name = 'thread'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = ThreadCommentForm()
        
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
                        comment.user_vote = ThreadCommentVote.objects.get(
                            comment=comment, user=self.request.user
                        ).value
                    except ThreadCommentVote.DoesNotExist:
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
        return context


@login_required
def thread_create_view(request):
    """Create new question thread."""
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(author=request.user)
            messages.success(request, 'Câu hỏi đã được đăng thành công!')
            return redirect('thread_list')
    else:
        form = ThreadForm()
    return render(request, 'threads/thread_form.html', {'form': form})


@login_required
def thread_update_view(request, pk):
    """Update existing thread (author only)."""
    thread = get_object_or_404(Thread, pk=pk)
    if thread.author != request.user:
        messages.error(request, 'Bạn không có quyền sửa câu hỏi này.')
        return redirect('thread_detail', pk=pk)
    
    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            thread = form.save(author=request.user)
            messages.success(request, 'Câu hỏi đã được cập nhật!')
            return redirect('thread_detail', pk=thread.pk)
    else:
        initial_hashtags = ', '.join([h.name for h in thread.hashtags.all()])
        form = ThreadForm(instance=thread, initial={'hashtag_names': initial_hashtags})
    return render(request, 'threads/thread_form.html', {'form': form, 'title': 'Chỉnh sửa câu hỏi'})


@login_required
def thread_delete_view(request, pk):
    """Delete thread (author only)."""
    thread = get_object_or_404(Thread, pk=pk)
    if thread.author != request.user:
        messages.error(request, 'Bạn không có quyền xóa câu hỏi này.')
        return redirect('thread_detail', pk=pk)
    
    if request.method == 'POST':
        thread.delete()
        messages.success(request, 'Câu hỏi đã được xóa!')
        return redirect('thread_list')
    return render(request, 'threads/thread_confirm_delete.html', {'thread': thread})


@login_required
def thread_comment_view(request, thread_pk):
    """Add nested comment to thread."""
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.method == 'POST':
        form = ThreadCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thread = thread
            comment.author = request.user
            comment.save()
            messages.success(request, 'Đã thêm bình luận!')
    return redirect('thread_detail', pk=thread_pk)


@login_required
def thread_comment_edit_view(request, comment_pk):
    """Edit own thread comment."""
    comment = get_object_or_404(ThreadComment, pk=comment_pk)
    
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
def thread_comment_delete_view(request, comment_pk):
    """
    Delete thread comment.
    Author can delete own comment. Thread owner can delete any comment.
    """
    comment = get_object_or_404(ThreadComment, pk=comment_pk)
    thread = comment.thread
    
    if comment.author != request.user and thread.author != request.user:
        return JsonResponse({'error': 'Bạn không có quyền xóa bình luận này.'}, status=403)
    
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def thread_comment_vote_view(request, comment_pk):
    """Vote on thread comment (up=1, down=-1)."""
    comment = get_object_or_404(ThreadComment, pk=comment_pk)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    value = int(request.POST.get('value', 0))
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote value'}, status=400)
    
    vote, created = ThreadCommentVote.objects.get_or_create(
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
def resolve_thread_view(request, thread_pk):
    """Mark thread as resolved (author only)."""
    thread = get_object_or_404(Thread, pk=thread_pk)
    if thread.author == request.user:
        thread.is_resolved = True
        thread.save()
        messages.success(request, 'Đã đánh dấu câu hỏi đã được giải quyết!')
    return redirect('thread_detail', pk=thread_pk)

def thread_hashtag_view(request, slug):
    """View threads filtered by hashtag."""
    hashtag = get_object_or_404(ThreadHashtag, slug=slug)
    threads = hashtag.threads.all().order_by('-created_at')
    return render(request, 'threads/hashtag_threads.html', {
        'hashtag': hashtag,
        'threads': threads,
    })