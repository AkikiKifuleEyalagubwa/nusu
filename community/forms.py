from django import forms
from .models import Tweet
from .widgets import MultipleFileInput

class TweetForm(forms.ModelForm):
    media = forms.FileField(
        widget=MultipleFileInput(),
        required=False,
        label='Add media'
    )

    class Meta:
        model = Tweet
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "What's happening?"
            }),
            'parent': forms.HiddenInput()
        }