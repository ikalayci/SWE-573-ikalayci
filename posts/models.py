# posts/models.py
from django.db import models
from django.contrib.auth.models import User



class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    wikidata_id = models.CharField(max_length=50, unique=True, null=True, blank=True)


    def __str__(self):
        return f"{self.name} (Wikidata ID: {self.wikidata_id})"





class Post(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        related_name="posts",
        null=True,
        blank=True
    )
    deleted_username = models.CharField(
        max_length=150, 
        default="",
        blank=True
    )
    title = models.CharField(max_length=255, null=False, blank=False)  # Required
    image = models.ImageField(upload_to='uploads/', null=False, blank=False)  # Required
    content = models.TextField(null=False, blank=False)  # Required
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    length = models.FloatField(null=True, blank=True)  # Optional
    width = models.FloatField(null=True, blank=True)   # Optional
    height = models.FloatField(null=True, blank=True)  # Optional
    weight = models.FloatField(null=True, blank=True)  # Optional
    price = models.FloatField(null=True, blank=True)   # Optional
    colors = models.TextField(null=True, blank=True)   # Optional
    
    era = models.CharField(max_length=2, choices=[('AC', 'AC'), ('BC', 'BC')], null=True, blank=True)
    time_period = models.CharField(max_length=100, null=True, blank=True)

    shapes = models.TextField(blank=True, null=True)
    materials = models.TextField(null=True, blank=True)  # Store as a string
    textures = models.TextField(blank=True, null=True)  # Stores textures as a comma-separated string

    status = models.CharField(
        max_length=10,
        choices=[('unsolved', 'Unsolved'), ('solved', 'Solved')],
        default='unsolved'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def get_username(self):
        if self.user:
            return self.user.username
        return self.deleted_username or "Deleted User"

    def __str__(self):
        return f"{self.title or 'No Title'} - {self.get_username()}"

    def get_shapes_list(self):
        """Utility method to return shapes as a list."""
        return self.shapes.split(',') if self.shapes else []
    #def get_textures_list(self):
    #    """Utility method to return textures as a list."""
    #    return self.textures.split(', ') if self.textures else []

    @property
    def time_period_display(self):
        """Format the time period for display"""
        if not self.time_period:
            return "Not Specified"
        
        parts = self.time_period.split('/')
        if len(parts) < 2:
            return self.time_period
            
        # Remove era (first element)
        parts = parts[1:]
        
        # If day is "00", remove it
        if len(parts) == 3 and parts[2] == "00":
            parts = parts[:2]
            
        # Reverse the order of the remaining parts
        parts.reverse()
        
        # If only year exists
        if len(parts) == 1:
            return parts[0]
        # If year and month exist
        elif len(parts) == 2:
            return f"{parts[0]}/{parts[1]}"
        # If year, month, and day exist
        elif len(parts) == 3:
            return f"{parts[0]}/{parts[1]}/{parts[2]}"
            
        return "Not Specified"

    @property
    def era_display(self):
        """Get the era part of the time period"""
        if not self.time_period:
            return "Not Specified"
            
        parts = self.time_period.split('/')
        return parts[0] if parts else "Not Specified"

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        related_name='comments',
        null=True,
        blank=True
    )
    deleted_username = models.CharField(
        max_length=150, 
        default="",
        blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def get_username(self):
        if self.user:
            return self.user.username
        return self.deleted_username or "Deleted User"

    def __str__(self):
        return f"Comment by {self.get_username()} on {self.post}"

