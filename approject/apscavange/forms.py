from django import forms
from django.forms import widgets
from .models import Seizure, InfoHistory, PasswordHash#, User

class LoginForm(forms.Form):
    username= forms.CharField(widget= forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
