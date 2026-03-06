"""Вспомогательные функции для приложения users."""

from django.core.mail import send_mail
from django.conf import settings


def send_confirmation_email(user, token):
    """
    Отправляет токен(код) подтверждения на email пользователя.
    Использует Django's email backend для отправки.
    В режиме разработки письма выводятся в консоль.
    Args:
        user: Объект пользователя.
        token: Токен подтверждения (от default_token_generator).
    """
    subject = 'Код подтверждения для YaMDb'
    message = f'Ваш код подтверждения: {token}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
