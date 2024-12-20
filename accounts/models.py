# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q

class Profile(models.Model):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, default='default-profile-picture.png')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='member')
    ranks = models.JSONField(default=list, blank=True)  # Store ranks as a JSON array

    def update_ranks(self):
        from posts.models import Post, Comment
        
        # Initialize new_ranks
        new_ranks = []
        
        # Not eligible if admin
        if not (self.user.is_superuser or self.user.is_staff):
            # Get all non-anonymous comments for the user
            user_comments = Comment.objects.filter(
                user=self.user,
                is_anonymous=False
            )
            
            # Count total comments
            total_user_comments = user_comments.count()
            
            # Check if any comment has votes or is a winner
            has_voted = user_comments.filter(
                Q(upvotes__gt=0) | 
                Q(downvotes__gt=0)
            ).exists()
            
            has_winning = user_comments.filter(won_posts__isnull=False).exists()
            
            # Check for Trailwhisper rank first (3+ comments AND at least one has votes AND no winning comments)
            if total_user_comments >= 3 and has_voted and not has_winning:
                new_ranks.append("Trailwhisper")
            # Then check for Trailblossom rank (3+ comments AND none have votes/wins)
            elif total_user_comments >= 3 and not has_voted and not has_winning:
                new_ranks.append("Trailblossom")
        
        # Calculate percentage of solved posts won by this user
        total_solved = Post.objects.exclude(winner_comment__isnull=True).count()
        if total_solved == 0:
            self.ranks = new_ranks  # Keep any existing ranks (like Trailblossom or Trailwhisper)
            self.save()
            return
        
        # Count winning comments that are not anonymous
        user_wins = Comment.objects.filter(
            user=self.user,
            won_posts__isnull=False,
            is_anonymous=False  # Exclude anonymous comments
        ).count()
        
        win_percentage = (user_wins / total_solved) * 100
        
        # Check for Mysterion rank
        is_mysteries_slayer = win_percentage >= 0.5  # 0.5% or more of total solved posts
        if is_mysteries_slayer:
            new_ranks = ["Mysterion"]  # Remove trailblossom and moderate if present
            
        # Only continue checking other ranks if not Mysterion
        elif not is_mysteries_slayer:
            # Calculate hint percentage for Hintarion rank
            total_hints = Comment.objects.filter(comment_type='hint', is_anonymous=False).count()
            if total_hints > 0:  # Only calculate if there are hints in the system
                user_hints = Comment.objects.filter(
                    user=self.user,
                    comment_type='hint',
                    is_anonymous=False  # Exclude anonymous hints
                ).count()
                hint_percentage = (user_hints / total_hints) * 100
                
                # Add Hintarion rank if threshold met
                if hint_percentage >= 0.5:  # 0.5% or more of total hints
                    if "Trailblossom" in new_ranks:
                        new_ranks.remove("Trailblossom")
                    if "Trailwhisper" in new_ranks:
                        new_ranks.remove("Trailwhisper")
                    new_ranks.append("Hintarion")
            
            # Calculate answer percentage for Luminarch rank
            total_answers = Comment.objects.filter(comment_type='answer', is_anonymous=False).count()
            if total_answers > 0:  # Only calculate if there are answers in the system
                user_answers = Comment.objects.filter(
                    user=self.user,
                    comment_type='answer',
                    is_anonymous=False  # Exclude anonymous answers
                ).count()
                answer_percentage = (user_answers / total_answers) * 100
                
                # Add Luminarch rank if threshold met
                if answer_percentage >= 0.5:  # 0.5% or more of total answers
                    if "Trailblossom" in new_ranks:
                        new_ranks.remove("Trailblossom")
                    if "Trailwhisper" in new_ranks:
                        new_ranks.remove("Trailwhisper")
                    new_ranks.append("Luminarch")

            # Calculate question percentage for Querysmith rank
            total_questions = Comment.objects.filter(comment_type='question', is_anonymous=False).count()
            if total_questions > 0:  # Only calculate if there are questions in the system
                user_questions = Comment.objects.filter(
                    user=self.user,
                    comment_type='question',
                    is_anonymous=False  # Exclude anonymous questions
                ).count()
                question_percentage = (user_questions / total_questions) * 100
                
                # Add Querysmith rank if threshold met
                if question_percentage >= 0.5:  # 0.5% or more of total questions
                    if "Trailblossom" in new_ranks:
                        new_ranks.remove("Trailblossom")
                    if "Trailwhisper" in new_ranks:
                        new_ranks.remove("Trailwhisper")
                    new_ranks.append("Querysmith")
            
            # Calculate percentage for Cloutcaster rank based on top voted comments
            total_posts = Post.objects.count()
            if total_posts > 0:  # Only calculate if there are posts in the system
                # Get comments that are in top voted lists (upvotes - downvotes)
                user_top_voted = Comment.objects.filter(
                    user=self.user,
                    is_anonymous=False,
                    upvotes__gt=0  # Only consider comments with upvotes
                ).order_by('-upvotes', 'downvotes')  # Order by most upvotes and least downvotes
                
                # Calculate the percentage
                top_voted_percentage = (user_top_voted.count() / total_posts) * 100
                
                # Add Cloutcaster rank if threshold met
                if top_voted_percentage >= 0.5:  # 0.5% or more of total posts
                    if "Trailblossom" in new_ranks:
                        new_ranks.remove("Trailblossom")
                    if "Trailwhisper" in new_ranks:
                        new_ranks.remove("Trailwhisper")
                    new_ranks.append("Cloutcaster")

            # Calculate percentage for Riddlecaster rank based on user's posts
            if total_posts > 0:  # Only calculate if there are posts in the system
                user_posts = Post.objects.filter(
                    user=self.user
                ).count()
                
                # Calculate the percentage
                post_percentage = (user_posts / total_posts) * 100
                
                # Add Riddlecaster rank if threshold met
                if post_percentage >= 0.5:  # 0.5% or more of total posts
                    if "Trailblossom" in new_ranks:
                        new_ranks.remove("Trailblossom")
                    if "Trailwhisper" in new_ranks:
                        new_ranks.remove("Trailwhisper")
                    new_ranks.append("Riddlecaster")
        
        self.ranks = new_ranks
        self.save()

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Set user_type based on user permissions
        user_type = 'admin' if (instance.is_superuser or instance.is_staff) else 'member'
        Profile.objects.create(user=instance, user_type=user_type)
    else:
        # Update existing profile's user_type if needed
        if hasattr(instance, 'profile'):
            correct_type = 'admin' if (instance.is_superuser or instance.is_staff) else 'member'
            if instance.profile.user_type != correct_type:
                instance.profile.user_type = correct_type
                instance.profile.save()

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