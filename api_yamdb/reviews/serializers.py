from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Comment, Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review

    def validate(self, data):
        """Валидация объекта отзыва."""
        request = self.context.get("request")
        title = self.context.get('title')
        if request.method == 'POST':
            if Review.objects.filter(
                author=request.user,
                title=title
            ).exists():
                raise serializers.ValidationError(
                    "Уже добавлен ваш отзыв к этому произведению."
                )
        return data

    def validate_score(self, value):
        """Валидация оценки произведения."""
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                "Поставьте оценку от 1 до 10."
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment
        read_only_fields = ('post',)
