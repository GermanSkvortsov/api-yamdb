"""Вспомогательные функции для приложения users."""

import random
import string


def generate_confirmation_code(length=6):
    """
    Генерирует случайный код подтверждения.
    По умолчанию 6 символов (цифры + буквы).
    """
    chars = string.digits + string.ascii_letters
    return ''.join(random.choices(chars, k=length))


def send_confirmation_email(user, code):
    """
    Отправляет код подтверждения на email пользователя.
    Пока просто печатает в консоль.
    """
    print(f"\n===== КОД ПОДТВЕРЖДЕНИЯ ДЛЯ {user.username} =====")
    print(f"Email: {user.email}")
    print(f"Код: {code}")
    print("=" * 40)
