"""Views для приложения users."""

from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError

from .models import User
from .serializers import (
    SignupSerializer, TokenSerializer, UserSerializer, MeSerializer
)
from .tokens import create_jwt_token
from .utils import generate_confirmation_code, send_confirmation_email
from .permissions import IsAdminOrUnauth401


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
                {'email': ['Этот username принадлежит другому email']},
                status=status.HTTP_400_BAD_REQUEST
            )

    except User.DoesNotExist:
        if User.objects.filter(email=email).exists():
            return Response(
                {'email': [
                    'Этот email уже зарегистрирован с другим username']},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.create_user(
                username=username,  # type: ignore
                email=email,
                password=None
            )
        except IntegrityError:
            return Response(
                {'error': ['Ошибка при создании пользователя']},
                status=status.HTTP_400_BAD_REQUEST
            )

    code = generate_confirmation_code()
    user.confirmation_code = code
    user.save(update_fields=['confirmation_code'])

    send_confirmation_email(user, code)

    return Response({
        'username': username, 'email': email}, status=status.HTTP_200_OK)


@api_view(['POST'])
def token(request):
    """
    Получение JWT-токена по коду подтверждения.
    Принимает username и confirmation_code.
    При успешной проверке возвращает JWT-токен и стирает код.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')  # type: ignore
    confirmation_code = serializer.validated_data.get(  # type: ignore
        'confirmation_code')

    # Ищем пользователя по username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'username': ['Пользователь не найден']},
            status=status.HTTP_404_NOT_FOUND
        )

    # Проверяем код подтверждения
    if user.confirmation_code != confirmation_code:
        return Response(
            {'confirmation_code': ['Неверный код подтверждения']},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Генерируем токен и стираем использованный код
    jwt_token = create_jwt_token(user)
    user.clear_confirmation_code()

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
    permission_classes = [IsAdminOrUnauth401]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)

    def get_permissions(self):
        """Определяем права доступа для разных действий."""
        if self.action == 'me':
            # Для /me/ используем только IsAuthenticated
            return [IsAuthenticated()]
        # Для всех остальных действий - базовые права
        return [permission() for permission in self.permission_classes]

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path='me'
    )
    def me(self, request):
        """Эндпоинт для работы с собственным профилем."""
        user = request.user

        if request.method == 'GET':
            serializer = MeSerializer(user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            # DELETE не разрешён для /me/
            return Response(
                {'detail': 'Метод "DELETE" не разрешен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

    def put(self, request, *args, **kwargs):
        """Запрещаем PUT запросы."""
        return Response(
            {'detail': 'Метод "PUT" не разрешен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
