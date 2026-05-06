"""
Views for exercises and solutions.
Path: apps/exercises/views.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from .models import Exercise, ExerciseHashtag, ExerciseComment, ExerciseVote, ExerciseCommentVote
from .forms import ExerciseForm, ExerciseCommentForm


def exercise_list_view(request):
    """Display exercises with search."""
    exercises = Exercise.objects.filter(status='APPROVED')
    
    search_query = request.GET.get('q', '')
    if search_query:
        exercises = exercises.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(author__username__icontains=search_query)
        )
    
    exercises = exercises.order_by('-created_at')
    
    if request.user.is_authenticated:
        for exercise in exercises:
            try:
                exercise.user_vote = ExerciseVote.objects.get(
                    exercise=exercise, user=request.user
                ).value
            except ExerciseVote.DoesNotExist:
                exercise.user_vote = 0
    else:
        for exercise in exercises:
            exercise.user_vote = 0
    
    context = {
        'exercises': exercises,
        'search_query': search_query,
        'search_action': '/exercises/',
    }
    return render(request, 'exercises/exercise_list.html', context)


def exercise_detail_view(request, pk):
    """Display single exercise with nested comments."""
    exercise = get_object_or_404(Exercise, pk=pk, status='APPROVED')
    
    all_comments = exercise.comments.all().order_by('created_at')
    
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
                    comment.user_vote = ExerciseCommentVote.objects.get(
                        comment=comment, user=request.user
                    ).value
                except ExerciseCommentVote.DoesNotExist:
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
    
    context = {
        'exercise': exercise,
        'comment_form': ExerciseCommentForm(),
        'comment_tree': comment_tree,
    }
    
    if request.user.is_authenticated:
        try:
            context['user_vote'] = ExerciseVote.objects.get(
                exercise=exercise, user=request.user
            ).value
        except ExerciseVote.DoesNotExist:
            context['user_vote'] = 0
    else:
        context['user_vote'] = 0
    
    return render(request, 'exercises/exercise_detail.html', context)


@login_required
def exercise_create_view(request):
    """Create new exercise."""
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(author=request.user)
            messages.success(request, 'Bài tập đã được đăng thành công!')
            return redirect('exercise_list')
    else:
        form = ExerciseForm()
    return render(request, 'exercises/exercise_form.html', {'form': form, 'title': 'Đăng bài tập mới'})


@login_required
def exercise_update_view(request, pk):
    """Update existing exercise (author only)."""
    exercise = get_object_or_404(Exercise, pk=pk)
    if exercise.author != request.user:
        messages.error(request, 'Bạn không có quyền sửa bài tập này.')
        return redirect('exercise_detail', pk=pk)
    
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            exercise = form.save(author=request.user)
            messages.success(request, 'Bài tập đã được cập nhật!')
            return redirect('exercise_detail', pk=exercise.pk)
    else:
        initial_hashtags = ', '.join([h.name for h in exercise.hashtags.all()])
        form = ExerciseForm(instance=exercise, initial={'hashtag_names': initial_hashtags})
    return render(request, 'exercises/exercise_form.html', {'form': form, 'title': 'Chỉnh sửa bài tập'})


@login_required
def exercise_delete_view(request, pk):
    """Delete exercise (author only)."""
    exercise = get_object_or_404(Exercise, pk=pk)
    if exercise.author != request.user:
        messages.error(request, 'Bạn không có quyền xóa bài tập này.')
        return redirect('exercise_detail', pk=pk)
    
    if request.method == 'POST':
        exercise.delete()
        messages.success(request, 'Bài tập đã được xóa!')
        return redirect('exercise_list')
    return render(request, 'exercises/exercise_confirm_delete.html', {'exercise': exercise})


@login_required
def exercise_comment_view(request, exercise_pk):
    """Add nested comment to exercise."""
    exercise = get_object_or_404(Exercise, pk=exercise_pk)
    if request.method == 'POST':
        form = ExerciseCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.exercise = exercise
            comment.author = request.user
            comment.save()
            messages.success(request, 'Đã thêm bình luận!')
    return redirect('exercise_detail', pk=exercise_pk)


@login_required
def exercise_comment_edit_view(request, comment_pk):
    """Edit own exercise comment."""
    comment = get_object_or_404(ExerciseComment, pk=comment_pk)
    
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
def exercise_comment_delete_view(request, comment_pk):
    """
    Delete exercise comment.
    Author can delete own comment. Exercise owner can delete any comment.
    """
    comment = get_object_or_404(ExerciseComment, pk=comment_pk)
    exercise = comment.exercise
    
    if comment.author != request.user and exercise.author != request.user:
        return JsonResponse({'error': 'Bạn không có quyền xóa bình luận này.'}, status=403)
    
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def exercise_comment_vote_view(request, comment_pk):
    """Vote on exercise comment (up=1, down=-1)."""
    comment = get_object_or_404(ExerciseComment, pk=comment_pk)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    value = int(request.POST.get('value', 0))
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote value'}, status=400)
    
    vote, created = ExerciseCommentVote.objects.get_or_create(
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
def exercise_vote_view(request, exercise_pk):
    """Vote on exercise (up=1, down=-1)."""
    exercise = get_object_or_404(Exercise, pk=exercise_pk)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    value = int(request.POST.get('value', 0))
    if value not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote value'}, status=400)
    
    vote, created = ExerciseVote.objects.get_or_create(
        exercise=exercise,
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
        'total_votes': exercise.total_votes(),
        'user_vote': value if value != 0 else 0
    })

def exercise_hashtag_view(request, slug):
    """View exercises filtered by hashtag."""
    hashtag = get_object_or_404(ExerciseHashtag, slug=slug)
    exercises = hashtag.exercises.filter(status='APPROVED').order_by('-created_at')
    return render(request, 'exercises/hashtag_exercises.html', {
        'hashtag': hashtag,
        'exercises': exercises,
    })