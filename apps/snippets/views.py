"""
Views for snippet management and listing.
Path: apps/snippets/views.py
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models as db_models
from django.http import JsonResponse
from .models import Snippet, SnippetComment, SnippetVote, SnippetCommentVote
from .forms import SnippetForm, SnippetCommentForm


def snippet_list_view(request):
    """Display all snippets with search and language filter."""
    snippets = Snippet.objects.all()
    
    search_query = request.GET.get('q', '')
    if search_query:
        snippets = snippets.filter(
            db_models.Q(title__icontains=search_query) |
            db_models.Q(description__icontains=search_query) |
            db_models.Q(content__icontains=search_query)
        )
    
    lang_filter = request.GET.get('lang', 'all')
    if lang_filter != 'all':
        snippets = snippets.filter(language=lang_filter)
    
    snippets = snippets.order_by('-created_at')
    
    context = {
        'snippets': snippets,
        'search_query': search_query,
        'lang_filter': lang_filter,
        'search_action': '/snippets/',
        'language_choices': Snippet.LANGUAGE_CHOICES,
    }
    return render(request, 'snippets/snippet_list.html', context)


def snippet_detail_view(request, pk):
    """Display single snippet with comments."""
    snippet = get_object_or_404(Snippet, pk=pk)
    snippet.views += 1
    snippet.save(update_fields=['views'])
    
    all_comments = snippet.comments.all().order_by('created_at')
    
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
    
    if request.user.is_authenticated:
        def add_user_votes(comments):
            for comment in comments:
                try:
                    comment.user_vote = SnippetCommentVote.objects.get(
                        comment=comment, user=request.user
                    ).value
                except SnippetCommentVote.DoesNotExist:
                    comment.user_vote = 0
                if hasattr(comment, 'children') and comment.children:
                    add_user_votes(comment.children)
        add_user_votes(comment_tree)
        
        try:
            user_vote = SnippetVote.objects.get(snippet=snippet, user=request.user).value
        except SnippetVote.DoesNotExist:
            user_vote = 0
    else:
        user_vote = 0
        for comment in comment_tree:
            comment.user_vote = 0
    
    context = {
        'snippet': snippet,
        'comment_form': SnippetCommentForm(),
        'comment_tree': comment_tree,
        'user_vote': user_vote,
    }
    return render(request, 'snippets/snippet_detail.html', context)


@login_required
def snippet_create_view(request):
    """Create new snippet."""
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(author=request.user)
            messages.success(request, 'Snippet đã được đăng thành công!')
            return redirect('snippet_list')
    else:
        form = SnippetForm()
    return render(request, 'snippets/snippet_form.html', {'form': form, 'title': 'Thêm snippet mới'})


@login_required
def snippet_update_view(request, pk):
    """Update existing snippet (author only)."""
    snippet = get_object_or_404(Snippet, pk=pk)
    if snippet.author != request.user:
        messages.error(request, 'Bạn không có quyền sửa snippet này.')
        return redirect('snippet_detail', pk=pk)
    
    if request.method == 'POST':
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            snippet = form.save(author=request.user)
            messages.success(request, 'Snippet đã được cập nhật!')
            return redirect('snippet_detail', pk=snippet.pk)
    else:
        form = SnippetForm(instance=snippet)
    return render(request, 'snippets/snippet_form.html', {'form': form, 'title': 'Chỉnh sửa snippet'})


@login_required
def snippet_delete_view(request, pk):
    """Delete snippet (author only)."""
    snippet = get_object_or_404(Snippet, pk=pk)
    if snippet.author != request.user:
        messages.error(request, 'Bạn không có quyền xóa snippet này.')
        return redirect('snippet_detail', pk=pk)
    
    if request.method == 'POST':
        snippet.delete()
        messages.success(request, 'Snippet đã được xóa!')
        return redirect('snippet_list')
    return render(request, 'snippets/snippet_confirm_delete.html', {'snippet': snippet})


@login_required
def snippet_comment_view(request, snippet_pk):
    """Add comment to snippet."""
    snippet = get_object_or_404(Snippet, pk=snippet_pk)
    if request.method == 'POST':
        form = SnippetCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.snippet = snippet
            comment.author = request.user
            comment.save()
            messages.success(request, 'Đã thêm bình luận!')
    return redirect('snippet_detail', pk=snippet_pk)


@login_required
def snippet_comment_edit_view(request, comment_pk):
    """Edit own snippet comment."""
    comment = get_object_or_404(SnippetComment, pk=comment_pk)
    
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
def snippet_comment_delete_view(request, comment_pk):
    """
    Delete snippet comment.
    Author can delete own comment. Snippet owner can delete any comment.
    """
    comment = get_object_or_404(SnippetComment, pk=comment_pk)
    snippet = comment.snippet
    
    if comment.author != request.user and snippet.author != request.user:
        return JsonResponse({'error': 'Bạn không có quyền xóa bình luận này.'}, status=403)
    
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def snippet_vote_view(request, snippet_pk):
    """Vote on snippet (up=1, down=-1)."""
    snippet = get_object_or_404(Snippet, pk=snippet_pk)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    value = int(request.POST.get('value', 0))
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote value'}, status=400)
    
    vote, created = SnippetVote.objects.get_or_create(
        snippet=snippet,
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
        'total_votes': snippet.total_votes(),
        'user_vote': value if value != 0 else 0
    })


@login_required
def snippet_comment_vote_view(request, comment_pk):
    """Vote on snippet comment (up=1, down=-1)."""
    comment = get_object_or_404(SnippetComment, pk=comment_pk)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    value = int(request.POST.get('value', 0))
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote value'}, status=400)
    
    vote, created = SnippetCommentVote.objects.get_or_create(
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