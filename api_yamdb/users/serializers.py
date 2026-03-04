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

    def validate_username(self, value):
        """Проверяем уникальность username при создании."""
        if self.instance is None:  # Это создание, а не обновление
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким именем уже существует.'
                )
        return value

    def validate_email(self, value):
        """Проверяем уникальность email при создании."""
        if self.instance is None:  # Это создание, а не обновление
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        return value

    def create(self, validated_data):
        """
        Создаёт пользователя без пароля.
        Использует кастомный метод модели create_user_without_password,
        который устанавливает unusable password.
        """
        # Создаём пользователя через кастомный метод
        return User.create_user_without_password(**validated_data)


class MeSerializer(BaseUserSerializer):
    """Для обычных пользователей — роль только для чтения."""

    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('role',)

    def validate_username(self, value):
        """Проверяем уникальность username при обновлении."""
        if self.instance and self.instance.username != value:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким именем уже существует.'
                )
        return value

    def validate_email(self, value):
        """Проверяем уникальность email при обновлении."""
        if self.instance and self.instance.email != value:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        return value

    def update(self, instance, validated_data):
        """
        Обновляет пользователя, но запрещает менять роль.
        Даже если кто-то попытается передать 'role' в запросе,
        мы удаляем это поле перед обновлением.
        """

        # Удаляем role из данных, если он там есть
        validated_data.pop('role', None)

        # Вызываем стандартный update родителя
        return super().update(instance, validated_data)


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
