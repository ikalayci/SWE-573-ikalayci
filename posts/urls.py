# posts/urls.py
from django.urls import path
from . import views, api

app_name = 'posts'

urlpatterns = [
    # API endpoints
    path('api/search-suggestions/', api.search_suggestions, name='search_suggestions'),
    
    # Regular views
    path('', views.post_list, name='post_list'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
]

