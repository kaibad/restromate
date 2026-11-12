from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
    'username',
    'first_name',
    'last_name',
    'email',
    'role',
    'is_staff',
    'is_active',
)

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

