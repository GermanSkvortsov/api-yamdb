from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

from .models import User
from .serializers import SignupSerializer
from .utils import generate_confirmation_code, send_confirmation_email


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
