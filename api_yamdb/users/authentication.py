"""Кастомная аутентификация по JWT-токену."""

import jwt
from rest_framework import authentication, exceptions
from django.conf import settings
from .models import User


class SafeJWTAuthentication(authentication.BaseAuthentication):
    """
    Кастомная аутентификация по JWT-токену.
    Проверяет токен в заголовке Authorization.
    """

    def authenticate(self, request):
        """
        Проверяет JWT-токен из заголовка Authorization.

        Возвращает пользователя и токен если всё ок,
        None если токена нет,
        Иначе вызывает AuthenticationFailed.
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None  # Важно: возвращаем None, а не исключение!

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            user = User.objects.get(id=payload['user_id'])
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Токен истёк')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Неверный токен')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Пользователь не найден')
