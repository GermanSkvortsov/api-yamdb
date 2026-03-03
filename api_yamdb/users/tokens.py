import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings


def create_jwt_token(user):
    """
    Создаёт JWT-токен для пользователя.
    Токен живёт 1 день.
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
    }

    token = jwt.encode(
        payload, 
        settings.SECRET_KEY,
        algorithm='HS256'
    )

    return token
