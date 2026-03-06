"""Вьюсеты для категорий, жанров и произведений."""

from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from users.permissions import IsAdminOrReadOnly
from .filters import TitleFilter
from .models import Category, Genre, Title
from .viewsets import CategoryGenreViewSet
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCreateSerializer,
)


class CategoryViewSet(CategoryGenreViewSet):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.annotate(
        rating=Avg(
            'reviews__score',
            default=None,
        )
    ).order_by('id')
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = TitleFilter
    search_fields = ('name', 'description',)
    ordering_fields = ('name', 'year', 'rating',)
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleCreateSerializer
