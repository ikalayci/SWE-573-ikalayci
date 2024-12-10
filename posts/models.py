# posts/models.py
from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255, null=False, blank=False)  # Required
    image = models.ImageField(upload_to='uploads/', null=False, blank=False)  # Required
    content = models.TextField(null=False, blank=False)  # Required
    length = models.FloatField(null=True, blank=True)  # Optional
    width = models.FloatField(null=True, blank=True)   # Optional
    height = models.FloatField(null=True, blank=True)  # Optional
    weight = models.FloatField(null=True, blank=True)  # Optional
    price = models.FloatField(null=True, blank=True)   # Optional
    colors = models.TextField(null=True, blank=True)   # Optional
    tags = models.ManyToManyField(Tag, blank=True)     # Optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"{self.title or 'No Title'} - {user_display}"


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"
