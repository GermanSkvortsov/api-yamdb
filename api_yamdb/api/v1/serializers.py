"""Сериализаторы для приложения users."""

from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User, validate_forbidden_username


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


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(
        read_only=True,
        default=None,
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        allow_empty=False,
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def to_representation(self, instance):
        """Возвращает полное представление произведения."""
        return TitleSerializer(instance, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        """Валидация объекта отзыва."""
        request = self.context.get('request')
        if request.method == 'POST':  # type: ignore
            if Review.objects.filter(
                author=request.user,  # type: ignore
                title=self.context.get(
                    'view').kwargs.get('title_id')).exists():
                raise serializers.ValidationError(
                    'Уже добавлен ваш отзыв к этому произведению.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
