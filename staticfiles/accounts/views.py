# accounts/views.py
from django.shortcuts import render, redirect
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
        return redirect('post_list')  # Redirect if already logged in

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('post_list')  # Redirect to post list after login
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
        return redirect('post_list')  # Redirect if already logged in

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')  # Capture the email field
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Ensure passwords match
        if password == password_confirm:
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
            else:
                # Create the user and log them in
                user = User.objects.create_user(username=username, email=email, password=password)
                # Create default profile for the user
                Profile.objects.get_or_create(user=user, defaults={"profession": "Unknown", "bio": "Unknown"})
                login(request, user)
                return redirect('post_list')  # Redirect to post list after successful registration
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
        return redirect('post_list')  # Redirect logged-in users to post list
    return render(request, 'accounts/home.html')

# Profile Page with Update Capability
@login_required
@csrf_exempt
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user, defaults={"profession": "Unknown", "bio": "Unknown"})

    if request.method == 'POST':
        try:
            # Handle JSON data for text fields
            if request.content_type == "application/json":
                data = json.loads(request.body)
                updated_fields = {}

                # Update username
                if 'username' in data:
                    username = data['username']
                    if username != user.username and User.objects.filter(username=username).exists():
                        return JsonResponse({'error': 'Username already exists'}, status=400)
                    user.username = username
                    updated_fields['username'] = username

                # Update email
                if 'email' in data:
                    email = data['email']
                    if email != user.email and User.objects.filter(email=email).exists():
                        return JsonResponse({'error': 'Email already exists'}, status=400)
                    user.email = email
                    updated_fields['email'] = email

                # Update profession
                if 'profession' in data:
                    profile.profession = data['profession'] or "Unknown"
                    updated_fields['profession'] = profile.profession

                # Update bio
                if 'bio' in data:
                    profile.bio = data['bio'] or "Unknown"
                    updated_fields['bio'] = profile.bio

                user.save()
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

    # Render the profile page
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile,
    })



