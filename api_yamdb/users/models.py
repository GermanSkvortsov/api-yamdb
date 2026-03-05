"""Модели приложения users."""

from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с ролями и bio."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )
    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )

    confirmation_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name='Код подтверждения'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

    def clean(self):
        """Запрещает использование username 'me' на уровне модели."""

        if self.username and self.username.lower() == 'me':
            raise ValidationError({
                'username': 'Имя "me" использовать запрещено'
            })
        super().clean()

    @property
    def is_admin(self):
        """Проверка, является ли пользователь администратором."""

        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверка, является ли пользователь модератором."""

        return self.role == self.MODERATOR

    @property
    def is_user(self):
        """Проверка, является ли пользователь обычным юзером."""

        return self.role == self.USER

    def clear_confirmation_code(self):
        """Стирает код подтверждения после использования."""

        self.confirmation_code = None
        self.save(update_fields=['confirmation_code'])
