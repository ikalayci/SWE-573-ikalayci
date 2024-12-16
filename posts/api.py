from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Tag

@csrf_exempt
def search_suggestions(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
        
    try:
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse([], safe=False)

        suggestions = []
        
        # Search in titles (up to 3 suggestions)
        title_results = Post.objects.filter(
            title__icontains=query
        ).values_list('title', flat=True).distinct()[:3]
        
        for title in title_results:
            suggestions.append({
                'text': title,
                'category': 'Title',
                'icon': '📄'
            })
        
        # Search in tags (up to 3 suggestions)
        tag_results = Tag.objects.filter(name__icontains=query).values_list('name', flat=True).distinct()[:3]
        for tag in tag_results:
            suggestions.append({
                'text': tag,
                'category': 'Tag',
                'icon': '🏷️'
            })
        
        # Search in colors (up to 2 suggestions)
        color_results = Post.objects.filter(
            colors__icontains=query
        ).values_list('colors', flat=True).distinct()[:2]
        for colors in color_results:
            color_list = [c.strip() for c in colors.split(',')]
            matching_colors = [c for c in color_list if query.lower() in c.lower()]
            for c in matching_colors:
                suggestions.append({
                    'text': c,
                    'category': 'Color',
                    'icon': '🎨'
                })

        # Search in dimensions and measurements
        dimension_fields = {
            'length': {'icon': '📏', 'suffix': ' cm'},
            'width': {'icon': '↔️', 'suffix': ' cm'},
            'height': {'icon': '↕️', 'suffix': ' cm'},
            'weight': {'icon': '⚖️', 'suffix': ' g'},
            'price': {'icon': '💰', 'suffix': ' $'}
        }

        for field, info in dimension_fields.items():
            try:
                # Try to convert query to float for exact matches
                query_num = float(query) if query.replace('.', '').isdigit() else None
                
                # Create a Q object for the field
                field_filter = Q(**{f"{field}__icontains": query})
                
                # If query is a valid number, also search for exact matches
                if query_num is not None:
                    field_filter |= Q(**{field: query_num})
                    
                    # Add range suggestions (±10% of the query value)
                    lower_bound = query_num * 0.9
                    upper_bound = query_num * 1.1
                    field_filter |= Q(**{f"{field}__gte": lower_bound, f"{field}__lte": upper_bound})

                # Get results using the combined filter
                results = Post.objects.filter(field_filter).values_list(field, flat=True).distinct()[:3]
                
                for value in results:
                    if value is not None:
                        # Format the value to 2 decimal places if it's not a whole number
                        formatted_value = f"{value:.2f}".rstrip('0').rstrip('.') if isinstance(value, float) else str(value)
                        suggestions.append({
                            'text': f"{formatted_value}{info['suffix']}",
                            'category': field.title(),
                            'icon': info['icon'],
                            'value': value  # Include the raw value for sorting
                        })

            except (ValueError, TypeError):
                # If the query isn't numeric, try partial string matching
                if len(query) >= 2:  # Only search if query is at least 2 characters
                    results = Post.objects.filter(**{f"{field}__icontains": query}) \
                                        .values_list(field, flat=True) \
                                        .distinct()[:3]
                    
                    for value in results:
                        if value is not None:
                            formatted_value = f"{value:.2f}".rstrip('0').rstrip('.') if isinstance(value, float) else str(value)
                            suggestions.append({
                                'text': f"{formatted_value}{info['suffix']}",
                                'category': field.title(),
                                'icon': info['icon'],
                                'value': value
                            })

        # Search in era (up to 2 suggestions)
        if 'bc' in query.lower() or 'ac' in query.lower():
            era_results = Post.objects.filter(
                era__icontains=query
            ).values_list('era', flat=True).distinct()[:2]
            for era in era_results:
                suggestions.append({
                    'text': era,
                    'category': 'Era',
                    'icon': '📅'
                })
        
        # Search in shapes (up to 2 suggestions)
        shape_results = Post.objects.filter(
            shapes__icontains=query
        ).values_list('shapes', flat=True).distinct()[:2]
        for shapes in shape_results:
            shape_list = [s.strip() for s in shapes.split(',')]
            matching_shapes = [s for s in shape_list if query.lower() in s.lower()]
            for s in matching_shapes:
                suggestions.append({
                    'text': s,
                    'category': 'Shape',
                    'icon': '📐'
                })

        # Search in textures (up to 2 suggestions)
        texture_results = Post.objects.filter(
            textures__icontains=query
        ).values_list('textures', flat=True).distinct()[:2]
        for textures in texture_results:
            texture_list = [t.strip() for t in textures.split(',')]
            matching_textures = [t for t in texture_list if query.lower() in t.lower()]
            for t in matching_textures:
                suggestions.append({
                    'text': t,
                    'category': 'Texture',
                    'icon': '🔲'
                })
        
        # Search in materials (up to 2 suggestions)
        material_results = Post.objects.filter(
            materials__icontains=query
        ).values_list('materials', flat=True).distinct()[:2]
        for material in material_results:
            material_list = [m.strip() for m in material.split(',')]
            matching_materials = [m for m in material_list if query.lower() in m.lower()]
            for m in matching_materials:
                suggestions.append({
                    'text': m,
                    'category': 'Material',
                    'icon': '🧱'
                })
        
        # Search in time periods (up to 2 suggestions)
        time_results = Post.objects.filter(
            time_period__icontains=query
        ).values_list('time_period', flat=True).distinct()[:2]
        for time in time_results:
            suggestions.append({
                'text': time,
                'category': 'Time Period',
                'icon': '📅'
            })

        # Search in content (up to 2 suggestions)
        content_results = Post.objects.filter(
            content__icontains=query
        ).values_list('content', flat=True).distinct()[:2]
        for content in content_results:
            position = content.lower().find(query.lower())
            start = max(0, position - 30)
            end = min(len(content), position + 30)
            snippet = "..." + content[start:end] + "..."
            suggestions.append({
                'text': snippet,
                'category': 'Content',
                'icon': '📝'
            })

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for item in suggestions:
            item_tuple = (item['text'], item['category'])
            if item_tuple not in seen:
                seen.add(item_tuple)
                unique_suggestions.append(item)

        return JsonResponse(unique_suggestions[:10], safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)