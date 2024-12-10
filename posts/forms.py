from django import forms
from .models import Post, Tag


class PostCreationForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Comma-separated tags',
            'class': 'form-control',
        })
    )

    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the title of your post',
            'class': 'form-control',
        })
    )
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write the story here...',
            'rows': 5,
            'style': 'height: 405px;'  # Inline height adjustment
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )
    length = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter length [cm]',
            'class': 'form-control',
        })
    )
    width = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter width [cm]',
            'class': 'form-control',
        })
    )
    height = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter height [cm]',
            'class': 'form-control',
        })
    )
    weight = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter weight (in grams)',
        })
    )
    colors = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Comma-separated colors',
            'class': 'form-control',
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'tags', 'colors', 'length', 'width', 'height', 'weight']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the title of your post',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write the story here...',
                'rows': 5,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'colors': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter colors (comma-separated)',
            }),
        }

    def save(self, commit=True, user=None):
        post = super().save(commit=False)
        if user:
            post.user = user
        if commit:
            # Save the post first to ensure it has a valid ID
            post.save()

            # Handle tags after saving the post
            tags_input = self.cleaned_data.get('tags', '')
            if tags_input:
                tag_names = [name.strip() for name in tags_input.split(',')]
                for name in tag_names:
                    if name:
                        tag, created = Tag.objects.get_or_create(name=name)
                        post.tags.add(tag)

        return post

