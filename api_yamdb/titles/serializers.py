"""Сериализаторы для категорий, жанров и произведений."""

from django.utils import timezone
from rest_framework import serializers

from .models import Category, Genre, Title


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
        required=False,
        allow_null=True,
    )
    description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        default='',
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )
        read_only_fields = ('id', 'rating')


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
        allow_empty=False
    )
    description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        default=''
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        extra_kwargs = {
            'description': {'allow_null': True, 'required': False}
        }

    def validate_year(self, value):
        """Проверяет, что год выпуска не больше текущего."""
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего'
            )
        return value

    def to_representation(self, instance):
        """Возвращает полное представление произведения."""
        return TitleSerializer(instance, context=self.context).data
