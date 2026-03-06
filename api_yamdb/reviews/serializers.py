"""Сериализаторы для отзывов и комментариев."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404

from reviews.models import Comment, Review
from titles.models import Title

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')#,'title')
        model = Review
        # # extra_kwargs = {'title': {'write_only': True}}
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Review.objects.all(),
        #         fields=['author', 'title'],
        #         message='Уже добавлен ваш отзыв к этому произведению.'
        #     )
        # ]

    def validate(self, data):
        """Валидация объекта отзыва."""
        request = self.context.get('request')
        if request.method == 'POST':  # type: ignore
            title_id=self.context.get('view').kwargs.get('title_id')
            title=get_object_or_404(Title,id=title_id)
            if Review.objects.filter(
                author=request.user,  # type: ignore
                title=title
            ).exists():
                raise serializers.ValidationError(
                    'Уже добавлен ваш отзыв к этому произведению.'
                )
        return data
    # def validate(self, data):
    #     """Валидация объекта отзыва."""
    #     request = self.context.get('request')
    #     if request.method == 'POST':  # type: ignore
    #         if Review.objects.filter(
    #             author=request.user,  # type: ignore
    #             title=self.context.get('view').get_title()
    #         ).exists():
    #             raise serializers.ValidationError(
    #                 'Уже добавлен ваш отзыв к этому произведению.'
    #             )
    #     return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
