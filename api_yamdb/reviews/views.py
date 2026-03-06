"""Вьюсеты для отзывов и комментариев."""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from titles.models import Title
from reviews.models import Review
from reviews.serializers import CommentSerializer, ReviewSerializer
from users.permissions import IsAuthorOrModeratorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        """Возвращает объект произведения по title_id из URL."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает отзывы для конкретного произведения."""
        return self.get_title().reviews.all()  # type: ignore

    # def get_serializer_context(self):
    #     """Добавляет произведение в контекст сериализатора."""
    #     context = super().get_serializer_context()
    #     context['title'] = self.get_title()
    #     return context

    def perform_create(self, serializer):
        """Cохраняет отзыв с автором и произведением."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        """Bозвращает объект отзыва по review_id и title_id"""
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        # return review
    # def get_review(self):
    #     """Bозвращает объект отзыва по review_id и title_id"""
    #     review_id = self.kwargs.get('review_id')
    #     title_id = self.kwargs.get('title_id')
    #     review = get_object_or_404(Review, id=review_id, title=title_id)
    #     return review

    def get_queryset(self):
        """Bозвращает комментарии для отзыва."""
        return self.get_review().comments.all()  # type: ignore

    def perform_create(self, serializer):
        """Cохраняет комментарий с автором и отзывом."""
        # review = self.get_review()
        serializer.save(author=self.request.user, review=self.get_review())
