"""Сериализаторы для приложения users."""

from rest_framework import serializers

from .models import User
from .validators import validate_username_not_me, validate_username_regex


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор с общими настройками."""

    username = serializers.CharField(
        max_length=150,
        validators=[validate_username_not_me, validate_username_regex]
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class UserSerializer(BaseUserSerializer):
    """Для админов — можно менять роль."""

    class Meta(BaseUserSerializer.Meta):
        pass


class MeSerializer(BaseUserSerializer):
    """Для обычных пользователей — роль только для чтения."""

    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('role',)


class SignupSerializer(serializers.Serializer):
    """Для регистрации."""
    username = serializers.CharField(
        max_length=150,
        validators=[validate_username_not_me, validate_username_regex]
    )
    email = serializers.EmailField(max_length=254)


class TokenSerializer(serializers.Serializer):
    """Для получения токена."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(write_only=True)
