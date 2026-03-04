"""Кастомные permissions для приложения users."""

from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated


class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов."""

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь администратором."""
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(permissions.BasePermission):
    """Доступ только для модераторов."""

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь модератором."""
        return request.user.is_authenticated and request.user.is_moderator


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Администратор может всё.
    Остальные только читать (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Определяет права доступа на уровне запроса."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Права для отзывов и комментариев:
    - Автор может редактировать/удалять своё
    - Модератор и админ могут редактировать/удалять всё
    - Остальные только читать
    """

    def has_object_permission(self, request, view, obj):
        """Определяет права доступа на уровне объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return (obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)


class IsAdminOrUnauth401(permissions.BasePermission):
    """
    Для UserViewSet:
    - Неаутентифицированные → 401
    - Аутентифицированные не-админы → 403
    - Админы → доступ
    """
    def has_permission(self, request, view):
        # Для /me/ своя логика (обрабатывается в get_permissions)
        if view.action == 'me':
            return True

        # Если пользователь не аутентифицирован
        if not request.user.is_authenticated:
            # ВСЕГДА кидаем NotAuthenticated для 401
            # DRF сам превратит это в 401, а нам не нужно думать о заголовках
            raise NotAuthenticated('Требуется аутентификация')

        # Если аутентифицирован, но не админ - будет 403
        if not request.user.is_admin:
            return False

        # Админ - доступ разрешён
        return True
