from django import forms
from django.forms import widgets
from .models import Seizure, InfoHistory, PasswordHash#, User

class LoginForm(forms.Form):
    username= forms.CharField(widget= forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

page_items_list = [
    (3, '3'),
    (5, '5'),
    (10, '10'),
    (20, '20'),
    ]

class PageItemsSelectForm(forms.Form):
    page_items = forms.ChoiceField(choices=page_items_list, initial=5)
    cur_page = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    max_page = forms.IntegerField(widget=forms.HiddenInput(), initial=1)

    # submit form on select item change
    #page_items.widget.attrs.update(onChange="form.submit();")


class SearchEmailForm(forms.Form):
    search_email = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Search for email'}), required=False)