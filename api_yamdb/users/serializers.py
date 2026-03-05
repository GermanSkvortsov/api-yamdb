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
            'role',
            'first_name',
            'last_name',
            'bio',
        )

    def validate_username(self, value):
        """
        Проверяет уникальность username при создании и обновлении.
        """
        # Если это обновление и username меняется
        if self.instance and self.instance.username != value:
            if User.objects.exclude(
                    pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким именем уже существует.'
                )
        # Если это создание
        elif self.instance is None:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким именем уже существует.'
                )
        return value

    def validate_email(self, value):
        """
        Проверяет уникальность email при создании и обновлении.
        """
        # Если это обновление и email меняется
        if self.instance and self.instance.email != value:
            if User.objects.exclude(
                    pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        # Если это создание
        elif self.instance is None:
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
