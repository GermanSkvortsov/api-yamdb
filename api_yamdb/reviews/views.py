from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Review
from reviews.serializers import CommentSerializer, ReviewSerializer
from titles.models import Title
from users.permissions import IsAuthorOrModeratorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        """Метод возвращает объект произведения по title_id из URL."""
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title

    def get_queryset(self):
        """Метод возвращает отзывы для конкретного произведения."""
        return self.get_title().reviews.all()

    def get_serializer_context(self):
        """Метод добавляет произведение в контекст сериализатора."""
        context = super().get_serializer_context()
        context['title'] = self.get_title()
        return context

    def perform_create(self, serializer):
        """Метод сохраняет отзыв с автором и произведением."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        """Метод возвращает объект отзыва по review_id и title_id"""
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review

    def get_queryset(self):
        """Метод возвращает комментарии для отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Метод сохраняет комментарий с автором и отзывом."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
