from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, MeSerializer, ReviewSerializer,
                          SignupSerializer, TitleCreateSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)
from .utils import send_confirmation_email
from .viewsets import CategoryGenreViewSet


@api_view(['POST'])
def signup(request):
    """Регистрация нового пользователя или повторный запрос кода."""
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')  # type: ignore
    email = serializer.validated_data.get('email')  # type: ignore

    try:
        user = User.objects.get(username=username)

        if user.email != email:
            return Response(
                {'username': ['Пользователь с таким username уже существует']},
                status=status.HTTP_400_BAD_REQUEST
            )

    except User.DoesNotExist:
        if User.objects.filter(email=email).exists():
            return Response(
                {'email': ['Пользователь с таким email уже существует']},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,  # type: ignore
            email=email,
            password=None
        )

    # Генерируем токен через default_token_generator (не храним в БД!)
    token = default_token_generator.make_token(user)

    # Отправляем email с токеном
    send_confirmation_email(user, token)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def token(request):
    """
    Получение JWT-токена по коду подтверждения.
    Принимает username и confirmation_code.
    При успешной проверке возвращает JWT-токен.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')  # type: ignore
    confirmation_code = serializer.validated_data.get(  # type: ignore
        'confirmation_code')

    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {'confirmation_code': ['Неверный код подтверждения']},
            status=status.HTTP_400_BAD_REQUEST
        )

    from rest_framework_simplejwt.tokens import AccessToken
    jwt_token = str(AccessToken.for_user(user))

    return Response({'token': jwt_token}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    - Админ может просматривать, создавать, изменять и удалять пользователей.
    - Обычные пользователи имеют доступ только к /me/.
    """

    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Эндпоинт для работы с собственным профилем."""
        user = request.user

        if request.method == 'GET':
            serializer = MeSerializer(user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


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

    def get_queryset(self):
        """Bозвращает комментарии для отзыва."""
        return self.get_review().comments.all()  # type: ignore

    def perform_create(self, serializer):
        """Cохраняет комментарий с автором и отзывом."""
        serializer.save(author=self.request.user, review=self.get_review())
