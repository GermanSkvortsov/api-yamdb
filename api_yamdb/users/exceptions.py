"""Кастомные обработчики исключений для DRF."""

from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений.

    DRF по умолчанию возвращает 403 для NotAuthenticated при использовании JWT.
    Это не соответствует HTTP спецификации (RFC 7235), где отсутствие
    аутентификации должно возвращать 401. Handler исправляет это поведение.
    """

    response = exception_handler(exc, context)

    if response is not None and isinstance(exc, NotAuthenticated):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response
