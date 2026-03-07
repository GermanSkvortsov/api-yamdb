"""Админка для приложения users."""

from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки админки для модели User."""

    list_display = (
        'username',
        'email',
        'role',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = ('role',)
    ordering = ('username',)
