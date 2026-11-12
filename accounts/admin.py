from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = list(UserAdmin.fieldsets or []) + [
        ('Role info', {
            'fields': ('role',),
        }),
    ]

    add_fieldsets = list(UserAdmin.add_fieldsets or []) + [
        ('Role info', {
            'fields': ('role',),
        }),
    ]

