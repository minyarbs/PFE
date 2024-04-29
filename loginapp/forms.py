from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput,TextInput

from loginapp.models import UploadedFile
class CreateUserForm(UserCreationForm):
    
    class Meta:
        model =User
        fields=['first_name','last_name','username', 'email','password1','password2','is_superuser']
        labels = {
            'is_superuser': 'Human Ressources'
        }

class LoginForm(AuthenticationForm):
    username=forms.CharField(widget=TextInput())
    password=forms.CharField(widget=PasswordInput())

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
