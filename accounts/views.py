# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .forms import UserUpdateForm, PasswordUpdateForm, ProfileUpdateForm, ProfilePictureForm
from .models import Profile, DeletedUser
from django.conf import settings
from posts.models import Post, Comment


# Login Code
def login_view(request):
    if request.user.is_authenticated:
        return redirect('posts:post_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(request, 'This account has been deactivated')
                return render(request, 'accounts/login.html')
        except User.DoesNotExist:
            pass
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('posts:post_list')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

# Logout Code
def logout_view(request):
    logout(request)
    return redirect('posts:post_list')  # Changed from 'home' to 'posts:post_list'

# Register Code
def register_view(request):
    if request.user.is_authenticated:
        return redirect('posts:post_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        is_admin = request.POST.get('role') == 'admin'

        # Check if trying to register as admin
        if is_admin:
            admin_key = request.POST.get('admin_key')
            admin_key_confirm = request.POST.get('admin_key_confirm')
            
            # Verify admin key
            if admin_key != 'SWE-573' or admin_key != admin_key_confirm:
                messages.error(request, 'Invalid or mismatched admin key')
                return render(request, 'accounts/register.html')

        if password == password_confirm:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
            else:
                # Create user
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # If admin role and correct key, set user as superuser
                if is_admin and admin_key == 'SWE-573':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()

                # Create profile
                Profile.objects.get_or_create(user=user, defaults={"profession": "Unknown", "bio": "Unknown"})
                
                login(request, user)
                return redirect('posts:post_list')
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
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile = user.profile
    # Force update ranks before displaying
    profile.update_ranks()
    
    # Determine user type
    if user.is_superuser or user.is_staff:
        user_type = 'Admin'
    else:
        user_type = profile.user_type
    
    context = {
        'profile': profile,
        'viewed_user': user,
        'username': user.username,
        'email': user.email,
        'profession': profile.profession,
        'bio': profile.bio,
        'user_type': user_type,  # Use the determined user type
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

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_screen(request):
    users = User.objects.all().order_by('username')
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin_screen.html', {
        'users': users,
        'posts': posts
    })

@user_passes_test(is_admin)
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Prevent modifying admin users
        if user.is_superuser:
            return JsonResponse({
                'success': False, 
                'error': 'Cannot modify admin status'
            })
        
        # Toggle the user's active status
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        return JsonResponse({
            'success': True,
            'message': f'User {status} successfully',
            'new_status': user.is_active
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@user_passes_test(is_admin)
@csrf_exempt
def delete_user(request, user_id):
    if request.method != 'DELETE':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed'
        }, status=405)
        
    try:
        user = get_object_or_404(User, id=user_id)
        
        if user.is_superuser:
            return JsonResponse({
                'success': False, 
                'error': 'Cannot delete admin users'
            }, status=403)
        
        # Check if DeletedUser record already exists
        if not DeletedUser.objects.filter(original_id=user.id).exists():
            DeletedUser.create_from_user(user)
        
        # Update posts
        Post.objects.filter(user=user).update(
            user=None,
            deleted_username="Deleted User"
        )
        
        # Update comments
        Comment.objects.filter(user=user).update(
            user=None,
            deleted_username="Deleted User"
        )
        
        # Delete profile and user
        if hasattr(user, 'profile'):
            try:
                user.profile.delete()
            except Profile.DoesNotExist:
                pass
                
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        print(f"Error deleting user: {str(e)}")  # For debugging
        return JsonResponse({
            'success': False,
            'error': f'Error deleting user: {str(e)}'
        }, status=500)

def profile(request):
    profile = request.user.profile
    
    # Determine user type
    if request.user.is_superuser or request.user.is_staff:
        user_type = 'Admin'
    else:
        user_type = profile.user_type
        
    context = {
        'profile': profile,
        'user_type': user_type,  # Add this to context
    }
    return render(request, 'accounts/profile.html', context)



