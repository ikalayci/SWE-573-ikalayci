from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    """Form to update username and email."""
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    """Form to update profession and bio."""
    class Meta:
        model = Profile
        fields = ['profession', 'bio']
        widgets = {
            'profession': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 150,
                'placeholder': 'Enter your profession',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'maxlength': 4000,
                'placeholder': 'Write a short bio about yourself',
                'rows': 5,  # Adjust the height of the textarea
            }),
        }

class PasswordUpdateForm(PasswordChangeForm):
    """Form to update the user's password."""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Current Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm New Password'
    )

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']