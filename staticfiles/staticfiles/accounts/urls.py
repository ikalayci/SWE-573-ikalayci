# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),  # Profile URL
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),  # Update Profile Picture URL
]
