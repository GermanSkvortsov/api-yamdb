"""Сериализаторы для приложения users."""

from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from .models import User, validate_forbidden_username


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор с общими настройками."""

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

    def validate_username(self, value):
        """Проверяет уникальность username при создании и обновлении."""
        if self.instance and self.instance.username == value:
            return value

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        return value

    def validate_email(self, value):
        """Проверяет уникальность email при создании и обновлении."""
        if self.instance and self.instance.email == value:
            return value

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return value


class UserSerializer(BaseUserSerializer):
    """Для админов — можно менять роль."""

    class Meta(BaseUserSerializer.Meta):
        pass

    def create(self, validated_data):
        """
        Создаёт пользователя с паролем (стандартный Django).
        Пароль генерируется автоматически и не используется для входа,
        но требуется для корректной работы стандартных механизмов Django.
        """
        return User.objects.create_user(**validated_data)


class MeSerializer(BaseUserSerializer):
    """Для обычных пользователей — роль только для чтения."""

    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('role',)

    def update(self, instance, validated_data):
        """
        Обновляет пользователя, но запрещает менять роль.
        Даже если кто-то попытается передать 'role' в запросе,
        мы удаляем это поле перед обновлением.
        """
        validated_data.pop('role', None)

        return super().update(instance, validated_data)


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
