# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),  # Profile URL
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),  # Update Profile Picture URL
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('admin-screen/', views.admin_screen, name='admin_screen'),
    path('api/toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('api/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]
