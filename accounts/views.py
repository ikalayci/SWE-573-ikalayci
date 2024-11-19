# accounts/views.py (libraries)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User # Came from Register Code
# Login Code
def login_view(request):
    if request.user.is_authenticated:
        return redirect('post_list')  # Redirect if already logged in

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
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
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        if password == password_confirm:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            else:
                user = User.objects.create_user(username=username, password=password)
                login(request, user)  # Log in the user after registration
                return redirect('post_list')  # Redirect to post list after registration
        else:
            messages.error(request, 'Passwords do not match')
    
    return render(request, 'accounts/register.html')

# myproject/views.py
# this code is homepage path

def home(request):
    if request.user.is_authenticated:
        return redirect('post_list')  # Redirect logged-in users to post list
    return render(request, 'accounts/home.html')


