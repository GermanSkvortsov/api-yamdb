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
        null=True,
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

    def save(self, *args, **kwargs):
        """
        Переопределённый метод сохранения с валидацией.
        Вызывает full_clean() перед сохранением, чтобы гарантировать,
        что все валидаторы (включая clean() с запретом 'me') будут выполнены
        при любом способе создания пользователя (админка, shell, скрипты).
        """

        self.full_clean()
        super().save(*args, **kwargs)

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

    @classmethod
    def create_user_without_password(cls, **kwargs):
        """
        Создаёт пользователя без пароля.
        Это альтернатива стандартному create_user,
        который требует пароль. Используется при создании
        пользователей через API (админом или при регистрации).
        Args:
            **kwargs: поля пользователя (username, email, и т.д.)
        Returns:
            User: созданный пользователь
        """

        # Создаём объект пользователя без сохранения
        user = cls(**kwargs)

        # Помечаем, что пароль не используется
        # set_unusable_password() устанавливает специальную метку
        # и делает непригодный для входа хэш
        user.set_unusable_password()

        # Сохраняем пользователя в БД
        user.save()

        return user
