"""Views для приложения users."""

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import IsAdmin
from .serializers import (
    MeSerializer,
    SignupSerializer,
    TokenSerializer,
    UserSerializer
)
from .utils import send_confirmation_email


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
