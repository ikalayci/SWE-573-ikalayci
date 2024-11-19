# posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Tag

@login_required
def create_post(request):
    # Clear all messages on each GET request to avoid showing old messages
    if request.method == 'GET':
        storage = messages.get_messages(request)
        storage.used = True  # Mark all messages as used to clear them

    # Handle post creation on POST request
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        tag_names = request.POST.getlist('tags')  # Retrieve all tag inputs as a list


        if image:
            post = Post.objects.create(user=request.user, content=content, image=image)
            for name in tag_names:
                name = name.strip()  # Clean up whitespace around the tag
                if name:  # Only add non-empty tags
                    tag, created = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)

            messages.success(request, 'Your post has been created!')
            return redirect('post_list')
        else:
            messages.error(request, 'An image is required to create a post.')
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

