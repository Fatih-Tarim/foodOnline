from django import forms
from accounts.models import User, UserProfile
from .validators import allow_only_images_validator

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

class UserProfileForm(forms.ModelForm):
    profile_pic = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model = UserProfile
        fields = ['profile_pic', 'cover_photo', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'pin_code', 'latitude', 'longitude']

    #longitude and latitude Readonly
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'

    