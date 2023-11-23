from django import forms
from accounts.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('first_name','last_name','username','email','password')

