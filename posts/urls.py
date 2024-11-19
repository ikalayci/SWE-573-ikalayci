# posts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('', views.post_list, name='post_list'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),  # New pattern for tag detail
]

