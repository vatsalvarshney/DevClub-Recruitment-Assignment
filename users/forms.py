from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class PfpChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']