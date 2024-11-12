# posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from django.contrib import messages

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Post.objects.create(user=request.user, content=content)
            messages.success(request, 'Your post has been created!')
            return redirect('post_list')
        else:
            messages.error(request, 'Content cannot be empty.')
    return render(request, 'posts/create_post.html')

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')  # Order by newest first
    return render(request, 'posts/post_list.html', {'posts': posts})

def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Check if user is authenticated; if not, set user as None
            user = request.user if request.user.is_authenticated else None
            Comment.objects.create(post=post, user=user, content=content)
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty.')
    return redirect('post_list')

