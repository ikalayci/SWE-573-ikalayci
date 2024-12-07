# posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Tag
from .forms import PostCreationForm


@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        tags = request.POST.get('tags', '')  # Tags from hidden input field

        post = Post.objects.create(title=title, content=content, image=image, user=request.user)
        tag_names = [tag.strip() for tag in tags.split(',')]
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)

        post.save()
        return redirect('post_list')

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

def tag_detail(request, tag_name):
    # View to display the message for each tag
    return render(request, 'posts/tag_detail.html', {'tag_name': tag_name})


