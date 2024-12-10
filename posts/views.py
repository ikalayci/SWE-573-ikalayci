from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Tag
from .forms import PostCreationForm


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostCreationForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False, user=request.user)

            try:
                # Validate dimensions
                length = request.POST.get('hidden_length', None)
                width = request.POST.get('hidden_width', None)
                height = request.POST.get('hidden_height', None)
                weight = request.POST.get('hidden_weight', None)
                if weight:
                    post.weight = float(weight)
                else:
                    post.weight = None  # Or any default value


                # Check if values are valid numbers
                post.length = float(length) if length and length.replace('.', '', 1).isdigit() else None
                post.width = float(width) if width and width.replace('.', '', 1).isdigit() else None
                post.height = float(height) if height and height.replace('.', '', 1).isdigit() else None
                post.weight = float(weight) if weight and weight.replace('.', '', 1).isdigit() else None
                post.price = float(request.POST.get('hidden_price')) if request.POST.get('hidden_price') else None
                post.colors = request.POST.get('colors', '')
                # Validate weight
                if post.weight is not None and post.weight <= 0:
                    raise ValueError("Weight must be a positive number.")
            except ValueError as e:
                messages.error(request, f"Invalid input: {e}")
                return render(request, 'posts/create_post.html', {'form': form})

            # Save the post to generate an ID
            post.save()

            # Handle tags
            tags = form.cleaned_data.get('tags', '')
            if tags:
                tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
          
            post.save()

            messages.success(request, "Post created successfully!")
            return redirect('post_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PostCreationForm()

    return render(request, 'posts/create_post.html', {'form': form})







def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    for post in posts:
        post.split_colors = post.colors.split(',') if post.colors else []
    return render(request, 'posts/post_list.html', {'posts': posts})


def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            user = request.user if request.user.is_authenticated else None
            Comment.objects.create(post=post, user=user, content=content)
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty.')
    return redirect('post_list')


def tag_detail(request, tag_name):
    return render(request, 'posts/tag_detail.html', {'tag_name': tag_name})
