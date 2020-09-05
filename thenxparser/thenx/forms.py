from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import password_validation
from django.utils.translation import gettext, gettext_lazy as _
from django import forms

class AuthenticationForm(BaseAuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True,
        'class': 'form-control',
        'placeholder': _('User')
    }))
    password = forms.CharField(strip=False,
                               widget=forms.PasswordInput(attrs={
                                   'autocomplete': 'current-password',
                                   'class': 'form-control',
                                   'placeholder': _("Password")
                               }))