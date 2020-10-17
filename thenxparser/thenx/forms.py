from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext, gettext_lazy as _
from django import forms
from .models import UploadCompetitors


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
#
# class upload_comps(forms.ModelForm):
#     # compfile = forms.FileField(
#     #     label="Select a file containing competitor URLS",
#     #     help_text='max. 500 megabytes'
#     # )
#
#     def __init__(self, *args, **kwargs):
#         super(upload_comps, self).__init__(*args, **kwargs)
#         self.fields['upload_file'].widget.attrs['class'] = 'fileUpload btn btn-outline-primary btn-lg btn-block'
#
#     class Meta:
#         model = UploadCompetitors
#         fields = [
#             'upload_file',
#         ]