"""Валидаторы для приложения users."""

from rest_framework import serializers


def validate_username_not_me(value):
    """
    Валидатор, запрещающий использовать 'me' в качестве username.
    Используется во всех сериализаторах, где есть поле username.
    """
    if value.lower() == 'me':
        raise serializers.ValidationError('Имя "me" использовать запрещено')
    return value
