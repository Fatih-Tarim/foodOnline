from django.contrib import admin
from accounts.models import User
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    list_display = ('email','username','first_name','last_name','role','is_admin','is_active')
    ordering = ('-date_joined',)

admin.site.register(User, CustomUserAdmin)