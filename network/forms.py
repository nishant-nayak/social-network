from django import forms
from .models import Post, Comment, Follower

class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Create a New Post',
                'class': 'form-control w-50 rounded',
                'rows': 5,
                'style': 'resize: none;'
            })
        }