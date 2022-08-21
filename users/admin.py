from django.contrib import admin

from django.contrib.auth.models import Group
from users.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserRegisterForm

class UserAdmin(BaseUserAdmin):
    add_form = UserRegisterForm
    list_display = ('username','roles')
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        ('Role(s)', {'fields': ('role',)}),
        ('Profile picture', {'fields': ('profile_picture',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
