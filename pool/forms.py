from django import forms
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Talk, Game, Team, City, Alert, PayerAudit, PickType, Pick, Talk, Winner, Week
from .validators import pool_username_validator

class CustomUserCreationForm(UserCreationForm):

    username = forms.CharField(max_length=150, validators=[pool_username_validator], help_text='Names and numbers only')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'mobile', 'first_name', 'last_name', 'image', 'favorite_team', 'timezone')

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
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile', 'image', 'favorite_team', 'timezone')

class PayerAuditForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())

    class Meta:
        model = PayerAudit
        fields = ('user', 'has_paid', 'payment_method', 'date_sent', 'date_received', 'message', )

class WinnerForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())
    week = forms.ModelChoiceField(queryset=Week.objects.all())

    class Meta:
        model = Alert
        fields = ('user', 'week', 'message',)

class AlertForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())

    class Meta:
        model = Alert
        fields = ('user', 'alert_level', 'effective_date', 'effective_end_date', 'message',)

class TalkAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())

    class Meta:
        model = Talk
        fields = ('user', 'message', 'effective_date', 'effective_end_date',)

class PickAdminForm(forms.ModelForm):
    
    class Meta:
        model = Pick
        fields = ('user', 'pick_type', 'score', )        

class PickForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())
    pick_type = forms.ModelChoiceField(queryset=PickType.objects.filter(is_active=True))
    score = forms.IntegerField(min_value=0, max_value=5)   
            
    class Meta:
        model = Pick
        fields = ('user', 'game', 'score', 'pick_type',)

class PickTypeAdminForm(forms.ModelForm):
    description = forms.TextInput()

    class Meta:
        model = PickType
        fields = ('description', 'name', 'value',)

class ScoresForm(forms.ModelForm):
    number = forms.IntegerField(disabled=True)
    start_time = forms.DateTimeField(disabled=True)
    home_team = forms.ModelChoiceField(queryset=Team.objects.all(), disabled=True)    
    visiting_team = forms.ModelChoiceField(queryset=Team.objects.all(), disabled=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), disabled=True)
    home_score = forms.IntegerField(max_value=99, label='Score')
    visitor_score = forms.IntegerField(max_value=99, label='Score')

    class Meta:
        model = Game
        fields = ('number', 'start_time', 'home_team', 'home_score', 'visiting_team', 'visitor_score', 'is_regulation_tie',)

class GameForm(forms.ModelForm):

    home_team = forms.ModelChoiceField(queryset=Team.objects.all())
    visiting_team = forms.ModelChoiceField(queryset=Team.objects.all())
    # city = forms.ModelChoiceField(queryset=City.objects.all())
    
    class Meta:
        model = Game
        fields = ('number', 'start_time', 'visiting_team', 'home_team', 'city',)

class TalkForm(forms.ModelForm):
    message = forms.TextInput()

    class Meta:
        model = Talk
        fields = ('message',)
