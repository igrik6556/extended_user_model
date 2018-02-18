# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthAdmin
from extuser.models import User, EmailConfirmation
from extuser.forms import UserChangeForm, UserCreationForm

from django.utils.translation import ugettext as _


class UserAdmin(AuthAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'username', 'is_confirm', 'is_superuser', 'is_staff',
                    'is_active', 'date_joined', 'last_login')
    list_filter = ('is_confirm', 'is_staff', 'is_active', 'is_superuser', 'date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)
    search_fields = ['username', 'email']
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'gender', 'birthday', 'avatar'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_confirm', 'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': ('date_joined', 'last_login')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


admin.site.register(EmailConfirmation)
admin.site.register(User, UserAdmin)
