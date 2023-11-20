from django.contrib import admin
from accounts.models import User, UserProfile
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.forms import UserCreationForm


class CustomUserAdmin(UserAdmin):
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    list_display = ('email','username','first_name','last_name','role','is_active','is_admin')
    ordering = ('-date_joined',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name','phone_number'),
        }),
    )



admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)