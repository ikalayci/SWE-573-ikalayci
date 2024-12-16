from django.urls import path, include

urlpatterns = [
    # ... your other URL patterns ...
    path('', include('posts.urls')),
] 