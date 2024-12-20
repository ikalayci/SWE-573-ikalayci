from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from posts.models import Post, Comment

class Command(BaseCommand):
    help = 'Clears all user data including posts, comments, and all user accounts'

    def handle(self, *args, **options):
        # Delete all comments
        self.stdout.write('Deleting all comments...')
        Comment.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all comments'))

        # Delete all posts
        self.stdout.write('Deleting all posts...')
        Post.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all posts'))

        # Delete all users including superusers
        self.stdout.write('Deleting all user accounts...')
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all user accounts'))

        self.stdout.write(self.style.SUCCESS('All user data has been cleared successfully')) 