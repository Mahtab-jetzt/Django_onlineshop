from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import user, Profile


@admin.register(user)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'is_staff',
        'is_active',
    )

    search_fields = ('username', 'email')

    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
            ),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone_number',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'phone_number',
    )