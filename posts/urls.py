# posts/urls.py
from django.urls import path
from . import views, api

app_name = 'posts'

urlpatterns = [
    path('', views.post_list, name='post_list'),  # Root URL shows post list
    # API endpoints - without 'posts/' prefix
    path('api/update-status/<int:post_id>/', views.update_post_status, name='update_post_status'),
    path('api/delete-post/<int:post_id>/', api.delete_post, name='delete_post'),
    path('api/delete-all-posts/', api.delete_all_posts, name='delete_all_posts'),
    path('api/vote-comment/<int:comment_id>/<str:vote_type>/', views.vote_comment, name='vote_comment'),
    path('api/search-suggestions/', api.search_suggestions, name='search_suggestions'),
    
    # Regular views
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('field-suggestions/', views.get_field_suggestions, name='field_suggestions'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]

