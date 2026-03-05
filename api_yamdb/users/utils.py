"""Вспомогательные функции для приложения users."""

import random
import string

from django.core.mail import send_mail
from django.conf import settings


def generate_confirmation_code(length=6):
    """
    Генерирует случайный код подтверждения.
    Args:
        length: Длина генерируемого кода (по умолчанию 6).
    Returns:
        str: Случайный код из цифр и букв латинского алфавита.
    """
    chars = string.digits + string.ascii_letters
    return ''.join(random.choices(chars, k=length))


def send_confirmation_email(user, code):
    """
    Отправляет код подтверждения на email пользователя.
    Использует Django's email backend для отправки.
    В режиме разработки письма выводятся в консоль.
    Args:
        user: Объект пользователя.
        code: Код подтверждения.
    """
    subject = 'Код подтверждения для YaMDb'
    message = f'Ваш код подтверждения: {code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
