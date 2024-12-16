from django import forms
from .models import Post, Tag


class PostCreationForm(forms.ModelForm):
    tags_with_links = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="JSON containing tags and their Wikidata IDs."
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
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
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
    price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter the price of the object',
            'class': 'form-control',
        })
    )
    time_period = forms.CharField(  # Optional time period
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter time period (e.g., BC 500/01/15)',
            'class': 'form-control',
        })
    )
    materials = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="JSON string of selected materials."
    )
    shapes = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="Comma-separated string of selected shapes."
    )
    textures = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="Comma-separated string of selected textures."
    )

    class Meta:
        model = Post
        fields = [
            'title', 'content', 'image', 'tags_with_links', 'colors',
            'length', 'width', 'height', 'weight', 'price', 'era', 'time_period',
            'materials', 'shapes', 'textures'
        ]
        widgets = {
            'colors': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter colors (comma-separated)',
            }),
            'era': forms.Select(choices=[('AC', 'AC'), ('BC', 'BC')], attrs={'class': 'form-control'}),
            'time_period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify time period'}),
            'materials': forms.HiddenInput(),
            'textures': forms.TextInput(attrs={'placeholder': 'Enter textures separated by commas'})
        }

    def clean_length(self):
        length = self.cleaned_data.get('length')
        if length and length < 0:
            raise forms.ValidationError("Length cannot be negative.")
        return length

    def clean_width(self):
        width = self.cleaned_data.get('width')
        if width and width < 0:
            raise forms.ValidationError("Width cannot be negative.")
        return width

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height and height < 0:
            raise forms.ValidationError("Height cannot be negative.")
        return height

    def save(self, commit=True, user=None):
        post = super().save(commit=False)
        if user:
            post.user = user
        if commit:
            post.save()
            post.shapes = self.cleaned_data.get('shapes', '')
            post.save()
            #post.textures = self.cleaned_data.get('textures', '')  # Save textures
            #post.save()
            tags_with_links_data = self.cleaned_data.get('tags_with_links', '[]')
            try:
                tags = json.loads(tags_with_links_data)
                for tag in tags:
                    name, wikidata_id = tag.get('label'), tag.get('id')
                    if name and wikidata_id:
                        tag_obj, _ = Tag.objects.get_or_create(
                            name=name,
                            defaults={'wikidata_id': wikidata_id}
                        )
                        post.tags.add(tag_obj)
            except json.JSONDecodeError:
                pass
        return post


