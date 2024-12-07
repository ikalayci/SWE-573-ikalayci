# posts/forms.py
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

    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write the story here...',
                'rows': 5,
                'style': 'height: 405px;'  # Inline height adjustment
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def save(self, commit=True, user=None):
        post = super().save(commit=False)
        if user:
            post.user = user
        if commit:
            post.save()

        # Handle tags
        tags_input = self.cleaned_data.get('tags', '')
        if tags_input:
            tag_names = [name.strip() for name in tags_input.split(',')]
            for name in tag_names:
                if name:
                    tag, created = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)

        return post
