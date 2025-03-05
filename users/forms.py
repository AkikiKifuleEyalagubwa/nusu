from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,UserProfile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'website', 'location']



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        
class CreateAgentForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

class SendTokensForm(forms.Form):
    username = forms.CharField()
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=1)