"""Сериализаторы для приложения users."""

from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from .models import User, validate_forbidden_username


class UserSerializer(serializers.ModelSerializer):
    """Для админов — можно менять роль."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'role',
            'first_name',
            'last_name',
            'bio',
        )


class MeSerializer(UserSerializer):
    """Для обычных пользователей — роль только для чтения."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignupSerializer(serializers.ModelSerializer):
    """Для регистрации."""

    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {
            'username': {'validators': [
                UnicodeUsernameValidator(),
                validate_forbidden_username,
            ]},
            'email': {'validators': []},
        }

    def validate(self, data):
        """Проверяет конфликты username и email."""
        username = data.get('username')
        email = data.get('email')

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if (user_by_username and user_by_email
                and user_by_username != user_by_email):
            raise serializers.ValidationError({
                'username': 'Пользователь с таким username уже существует',
                'email': 'Пользователь с таким email уже существует'
            })

        return data

    def create(self, validated_data):
        """Создаёт пользователя без пароля (он не нужен для входа)."""
        return User.objects.create_user(**validated_data, password=None)


class TokenSerializer(serializers.Serializer):
    """Для получения токена."""

    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        write_only=True
    )
    confirmation_code = serializers.CharField(write_only=True)
