# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import UserUpdateForm, PasswordUpdateForm, ProfileUpdateForm, ProfilePictureForm
from .models import Profile
from django.conf import settings


# Login Code
def login_view(request):
    if request.user.is_authenticated:
        return redirect('posts:post_list')  # Changed from 'home' to 'posts:post_list'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('posts:post_list')  # Changed from 'home' to 'posts:post_list'
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

# Logout Code
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to homepage after logout

# Register Code
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Changed from 'post_list' to 'home'

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password == password_confirm:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                Profile.objects.get_or_create(user=user, defaults={"profession": "Unknown", "bio": "Unknown"})
                login(request, user)
                return redirect('home')  # Changed from 'post_list' to 'home'
        else:
            messages.error(request, 'Passwords do not match')
    
    return render(request, 'accounts/register.html')

def update_profile_picture(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page
    else:
        form = ProfilePictureForm(instance=request.user.profile)
    return render(request, 'update_profile_picture.html', {'form': form})

# Home Page
def home(request):
    if request.user.is_authenticated:
        return render(request, 'accounts/home.html')  # Changed from redirect('post_list')
    return render(request, 'accounts/home.html')

# Profile Page with Update Capability
@csrf_exempt
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        profile_user = request.user
    
    profile = profile_user.profile
    
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.id != profile_user.id:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
            
        try:
            # Handle JSON data for text fields
            if request.content_type == "application/json":
                data = json.loads(request.body)
                updated_fields = {}

                # Update username
                if 'username' in data:
                    username = data['username']
                    if username != request.user.username and User.objects.filter(username=username).exists():
                        return JsonResponse({'error': 'Username already exists'}, status=400)
                    request.user.username = username
                    updated_fields['username'] = username

                # Update email
                if 'email' in data:
                    email = data['email']
                    if email != request.user.email and User.objects.filter(email=email).exists():
                        return JsonResponse({'error': 'Email already exists'}, status=400)
                    request.user.email = email
                    updated_fields['email'] = email

                # Update profession
                if 'profession' in data:
                    profile.profession = data['profession'] or "Unknown"
                    updated_fields['profession'] = profile.profession

                # Update bio
                if 'bio' in data:
                    profile.bio = data['bio'] or "Unknown"
                    updated_fields['bio'] = profile.bio

                # Update password
                if 'current_password' in data and 'new_password' in data:
                    if not request.user.check_password(data['current_password']):
                        return JsonResponse({'error': 'Current password is incorrect'}, status=400)
                    request.user.set_password(data['new_password'])
                    updated_fields['password'] = 'updated'

                request.user.save()
                profile.save()
                return JsonResponse(updated_fields)

            # Handle image file upload
            elif request.content_type.startswith("multipart/form-data"):
                profile_picture = request.FILES.get('image')
                if profile_picture:
                    profile.profile_picture = profile_picture
                    profile.save()
                    return JsonResponse({'success': True, 'profile_picture_url': profile.profile_picture.url})
                return JsonResponse({'error': 'No image uploaded'}, status=400)

            return JsonResponse({'error': 'Invalid content type'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'debug': settings.DEBUG,
        'is_own_profile': request.user.id == profile_user.id if request.user.is_authenticated else False
    }
    
    return render(request, 'accounts/profile.html', context)

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=profile_user)
    
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'is_own_profile': request.user == profile_user
    })



