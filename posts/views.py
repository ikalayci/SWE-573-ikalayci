import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Tag
from .forms import PostCreationForm
from django.db.models import Q
from django.http import JsonResponse



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
            return redirect('posts:post_list')
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = PostCreationForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    
    if request.GET.get('advanced_search'):
        # Handle categorized information filters
        for field in ['tags', 'colors', 'shapes', 'materials', 'textures']:
            filters = request.GET.get(f'{field}_filters', '').split(',')
            filters = [f.strip() for f in filters if f.strip()]
            
            if filters:
                if 'Not Specified!' in filters:
                    if field == 'tags':
                        posts = posts.filter(tags__isnull=True)
                    else:
                        posts = posts.filter(
                            Q(**{f'{field}__isnull': True}) | 
                            Q(**{f'{field}': ''}) |
                            Q(**{f'{field}__exact': ' '})
                        )
                else:
                    for filter_value in filters:
                        if field == 'tags':
                            posts = posts.filter(tags__name=filter_value)
                        else:
                            posts = posts.filter(**{f'{field}__icontains': filter_value})

        # Handle quantifiable properties (min/max filters)
        field_mappings = {
            'length': 'length',
            'width': 'width',
            'height': 'height',
            'weight': 'weight',
            'price': 'price'
        }
        
        for form_field, db_field in field_mappings.items():
            min_value = request.GET.get(f'min_{form_field}', '').strip()
            max_value = request.GET.get(f'max_{form_field}', '').strip()
            
            # Skip if both values are empty
            if not min_value and not max_value:
                continue

            try:
                # Convert values to float if they exist
                min_val = float(min_value) if min_value else None
                max_val = float(max_value) if max_value else None

                # Validate min <= max if both exist
                if min_val is not None and max_val is not None:
                    if min_val > max_val:
                        messages.error(
                            request, 
                            f'Error: Minimum value ({min_val}) cannot be greater than maximum value ({max_val}) for {form_field.title()}'
                        )
                        return redirect('posts:post_list')

                # Apply filters based on what values exist
                if min_val is not None and max_val is not None:
                    # Both min and max: filter for values between them
                    posts = posts.filter(
                        **{f'{db_field}__gte': min_val, 
                           f'{db_field}__lte': max_val}
                    ).exclude(**{f'{db_field}__isnull': True})
                elif min_val is not None:
                    # Only min: filter for values >= min
                    posts = posts.filter(
                        **{f'{db_field}__gte': min_val}
                    ).exclude(**{f'{db_field}__isnull': True})
                elif max_val is not None:
                    # Only max: filter for values <= max
                    posts = posts.filter(
                        **{f'{db_field}__lte': max_val}
                    ).exclude(**{f'{db_field}__isnull': True})

            except ValueError:
                messages.error(
                    request, 
                    f'Error: Please enter valid numbers for {form_field.title()}'
                )
                return redirect('posts:post_list')

        # Handle Time Period filters
        era = request.GET.get('era', '').strip()
        min_year = request.GET.get('min_time_period', '').strip()
        max_year = request.GET.get('max_time_period', '').strip()
        min_month = request.GET.get('min_month', '').strip()
        max_month = request.GET.get('max_month', '').strip()
        min_day = request.GET.get('min_day', '').strip()
        max_day = request.GET.get('max_day', '').strip()

        # Handle time period filtering
        if min_year or max_year or era:
            try:
                # Filter by Era first if selected
                if era:
                    posts = posts.filter(era=era)

                # Build date strings
                min_date = None
                max_date = None

                if min_year:
                    # Ensure consistent format: YYYY
                    min_date = min_year.zfill(4)
                    if min_month:
                        min_date += f"/{min_month.zfill(2)}"
                        if min_day:
                            min_date += f"/{min_day.zfill(2)}"

                if max_year:
                    # Ensure consistent format: YYYY
                    max_date = max_year.zfill(4)
                    if max_month:
                        max_date += f"/{max_month.zfill(2)}"
                        if max_day:
                            max_date += f"/{max_day.zfill(2)}"

                # Validate dates if both exist
                if min_date and max_date:
                    min_parts = min_date.split('/')
                    max_parts = max_date.split('/')
                    
                    # Compare years first
                    min_year_val = int(min_parts[0])
                    max_year_val = int(max_parts[0])
                    
                    if min_year_val > max_year_val:
                        messages.error(request, 'Error: Minimum year cannot be later than maximum year')
                        return redirect('posts:post_list')

                    # Apply date range filter
                    posts = posts.exclude(time_period__isnull=True).exclude(time_period='')
                    posts = posts.filter(time_period__gte=min_date)
                    posts = posts.filter(time_period__lte=max_date)

                elif min_date:
                    # Only min date: get posts with later dates
                    posts = posts.exclude(time_period__isnull=True).exclude(time_period='')
                    # Filter for posts with time_period greater than or equal to min_date
                    posts = posts.filter(time_period__gte=min_date)

                elif max_date:
                    # Only max date: get posts with earlier dates
                    posts = posts.exclude(time_period__isnull=True).exclude(time_period='')
                    # Filter for posts with time_period less than or equal to max_date
                    posts = posts.filter(time_period__lte=max_date)

            except ValueError:
                messages.error(request, 'Error: Please enter valid numbers for dates')
                return redirect('posts:post_list')

    # Process post attributes
    for post in posts:
        post.split_colors = post.colors.split(',') if post.colors else []
        post.split_materials = post.materials.split(', ') if post.materials else []
        post.split_textures = [texture.strip() for texture in post.textures.split(',')] if post.textures and post.textures.strip() else []
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
    return redirect('posts:post_list')


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


def get_field_suggestions(request):
    field = request.GET.get('field')
    query = request.GET.get('q', '').strip().lower()
    suggestions = []
    
    if not field:
        return JsonResponse({'suggestions': []})
    
    # Get unique values for the specified field
    if field == 'tags':
        # For tags, search in the Tag model
        suggestions = list(Tag.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True).distinct()[:5])
        
        # Add "Not Specified!" if there are posts without tags and query matches
        if ('not' in query or 'specified' in query) and Post.objects.filter(tags__isnull=True).exists():
            suggestions.insert(0, "Not Specified!")
    else:
        # For other fields (colors, shapes, materials, textures)
        field_values = Post.objects.all()
        
        if field in ['colors', 'materials', 'shapes', 'textures']:
            # Split the comma-separated values and get unique items
            all_values = []
            empty_field_exists = False
            
            for post in field_values:
                value = getattr(post, field, '')
                if not value or value.isspace():
                    empty_field_exists = True
                    continue
                values = value.split(',')
                all_values.extend([v.strip() for v in values if v.strip()])
            
            # Filter and get unique values
            unique_values = set(all_values)
            suggestions = [v for v in unique_values if query.lower() in v.lower()][:5]
            
            # Add "Not Specified!" if there are empty fields and query matches
            if empty_field_exists and ('not' in query or 'specified' in query):
                suggestions.insert(0, "Not Specified!")
    
    return JsonResponse({'suggestions': suggestions})

