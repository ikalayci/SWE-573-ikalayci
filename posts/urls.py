# posts/urls.py
from django.urls import path
from . import views, api

app_name = 'posts'

urlpatterns = [
    # API endpoints
    path('api/search-suggestions/', api.search_suggestions, name='search_suggestions'),
    path('api/update-status/<int:post_id>/', api.update_post_status, name='update_status'),
    
    # Regular views
    path('', views.post_list, name='post_list'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('field-suggestions/', views.get_field_suggestions, name='field_suggestions'),
]

