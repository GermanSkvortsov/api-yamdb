"""Модели приложения users."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


MAX_LENGTH_ROLE = 20
MAX_LENGTH_USERNAME = 150


def validate_forbidden_username(value):
    """Запрещает использование запрещенных имен пользователя."""
    if value.lower() in settings.FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'Имя "{value}" использовать запрещено'
        )


class User(AbstractUser):
    """Кастомная модель пользователя с ролями и bio."""

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )

    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_forbidden_username],
        verbose_name='Username'
    )
    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=MAX_LENGTH_ROLE,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверка, является ли пользователь администратором."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверка, является ли пользователь модератором."""
        return self.role == self.Role.MODERATOR
