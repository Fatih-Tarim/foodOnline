from django import forms
from accounts.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('first_name','last_name','username','email','password')
    
    #This super func. will give an ability to override this clean() method
    def clean(self):
        cleaned_data= super(UserForm, self).clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        #This called non field error
        if password != password_confirm:
            raise forms.ValidationError(
                'Password does not match!'
            )

