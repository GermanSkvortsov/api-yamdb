"""Валидаторы для приложения users."""

from django.core.validators import RegexValidator
from rest_framework import serializers


def validate_username_not_me(value):
    """
    Валидатор, запрещающий использовать 'me' в качестве username.
    Используется во всех сериализаторах, где есть поле username.
    """
    if value.lower() == 'me':
        raise serializers.ValidationError('Имя "me" использовать запрещено')
    return value


def validate_username_regex(value):
    """
    Проверяет, что username содержит только допустимые символы.
    Допустимы: буквы, цифры, и символы @/./+/-/_
    """
    regex_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message='Username может содержать только буквы, '
                'цифры и символы @/./+/-/_'
    )
    regex_validator(value)
    return value
