"""Кастомные permissions для приложения users."""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Администратор может всё.
    Остальные только читать (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Определяет права доступа на уровне запроса."""
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and request.user.is_admin)
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Права для отзывов и комментариев:

    - Автор может редактировать/удалять своё
    - Модератор и админ могут редактировать/удалять всё
    - Остальные только читать
    - Неаутентифицированные пользователи получают 401 для небезопасных методов
    """

    def has_permission(self, request, view):
        """Определяет права доступа на уровне запроса."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Определяет права доступа на уровне объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return (
            request.user.is_moderator
            or request.user.is_admin
            or obj.author == request.user
        )


class IsAdmin(permissions.BasePermission):
    """
    Доступ только для администраторов.
    Для /me/ используется отдельное разрешение.
    """

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь администратором."""
        return request.user.is_authenticated and request.user.is_admin
