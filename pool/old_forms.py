from django import forms
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Talk

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'mobile', 'first_name', 'last_name', 'image', 'favorite_team')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'mobile')

class EditUserForm(forms.ModelForm):
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Username'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'First'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Last'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Email'}))
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Numbers Only'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile', 'image', 'favorite_team')

class TalkForm(forms.ModelForm):

    message = forms.TextInput()
    
    # effective_date = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Talk
        fields = ('message', )

