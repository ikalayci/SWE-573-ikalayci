import json
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
            colors = request.POST.get('colors', '')  # Colors from hidden input field
            materials = request.POST.getlist('materials[]')
            
            try:
                # Validate and assign dimensions
                length = request.POST.get('hidden_length', None)
                width = request.POST.get('hidden_width', None)
                height = request.POST.get('hidden_height', None)
                weight = request.POST.get('hidden_weight', None)

                post.length = float(length) if length and length.replace('.', '', 1).isdigit() else None
                post.width = float(width) if width and width.replace('.', '', 1).isdigit() else None
                post.height = float(height) if height and height.replace('.', '', 1).isdigit() else None
                post.weight = float(weight) if weight and float(weight) > 0 else None

                # Validate and assign price
                post.price = float(request.POST.get('hidden_price')) if request.POST.get('hidden_price') else None




                # Assign time period
                era = request.POST.get('era', '').strip()
                assigned_time = request.POST.get('assigned_time', '').strip()
                time_period = request.POST.get('time_period', '').strip()

            except ValueError as e:
                messages.error(request, f"Invalid input: {e}")
                return render(request, 'posts/create_post.html', {'form': form})
            
                # Save to the post model
            post.era = era
            post.time_period = time_period

            post.colors = colors  # Assuming 'colors' is a field in the Post model
            post.materials = ", ".join(materials) if materials else None  # Store as a string
            post.shapes = form.cleaned_data.get('shapes', '')
            #textures = request.POST.get('textures', '')
            #post.textures = ", ".join(textures.split(',')) if textures else None
            post.textures = form.cleaned_data.get('textures', '')  # Save textures manually

            # Save the post
            post.save()

            # Save tags with Wikidata linkage
            tags_with_links_data = form.cleaned_data.get('tags_with_links', '[]')
            try:
                tags = json.loads(tags_with_links_data)
                for tag in tags:
                    name = tag.get('label')
                    wikidata_id = tag.get('id')
                    if name and wikidata_id:
                        tag_obj, created = Tag.objects.get_or_create(
                            name=name,
                            defaults={'wikidata_id': wikidata_id}
                        )
                        post.tags.add(tag_obj)
            except json.JSONDecodeError:
                messages.error(request, "Error parsing tags. Please try again.")

            messages.success(request, "Post created successfully!")
            return redirect('post_list')
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = PostCreationForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    for post in posts:
        # Process colors
        post.split_colors = post.colors.split(',') if post.colors else []
        
        # Process materials
        post.split_materials = post.materials.split(', ') if post.materials else []
        
        # Process textures
        post.split_textures = [texture.strip() for texture in post.textures.split(',')] if post.textures and post.textures.strip() else []
        
        # Get user profile picture
        post.user_profile_pic = post.user.profile.profile_picture if hasattr(post.user, 'profile') and post.user.profile.profile_picture else None
        
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
    tag = get_object_or_404(Tag, name=tag_name)
    posts = tag.post_set.all()
    return render(request, 'posts/tag_detail.html', {'tag_name': tag_name, 'posts': posts})


def categorize_color(hex_color):
    # Convert hex to RGB
    rgb = int(hex_color[1:], 16)
    r, g, b = (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF

    # Apply the categorization rules (similar to the JavaScript function)
    if r > 1.2 * g and r > 1.2 * b:
        return "Red"
    if r > g and b > g and r >= 1.5 * b:
        return "Pink"
    if r > g and g > b:
        return "Orange"
    if r >= g and b < 0.5 * (r + g):
        return "Yellow"
    if g > 1.2 * r and g > 1.2 * b:
        return "Green"
    if b > 1.2 * r and b > 1.2 * g:
        return "Blue"
    if r >= b and r > g and b > g:
        return "Purple"
    if r > g and g > b and r + g + b < 384:
        return "Brown"
    if abs(r - g) < 20 and abs(g - b) < 20 and r + g + b < 128:
        return "Black"
    if abs(r - g) < 20 and abs(g - b) < 20 and r + g + b > 700:
        return "White"
    if abs(r - g) < 20 and abs(g - b) < 20:
        return "Gray"
    if g == b and g > r:
        return "Cyan and Teal"
    return "Neutral"


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Process the same attributes as in post_list view
    post.split_colors = post.colors.split(',') if post.colors else []
    post.split_materials = post.materials.split(', ') if post.materials else []
    post.split_textures = [texture.strip() for texture in post.textures.split(',')] if post.textures and post.textures.strip() else []
    post.user_profile_pic = post.user.profile.profile_picture if hasattr(post.user, 'profile') and post.user.profile.profile_picture else None
    
    return render(request, 'posts/post_detail.html', {'post': post})

