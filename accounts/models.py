# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, default='default-profile-picture.png')

    def __str__(self):
        return self.user.username
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class DeletedUser(models.Model):
    original_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=150)
    deletion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deleted: {self.username}"

    @classmethod
    def create_from_user(cls, user):
        return cls.objects.create(
            original_id=user.id,
            username=user.username
        )