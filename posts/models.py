# posts/models.py
from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

#class Post(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    title = models.CharField(max_length=255)  # Add this field
#    content = models.TextField()
#    image = models.ImageField(upload_to='uploads/')
#    tags = models.ManyToManyField(Tag, blank=True)
#    created_at = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)  # Ensure title field exists
    content = models.TextField()
    image = models.ImageField(upload_to='uploads/')
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or 'No Title'} - {self.user.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

