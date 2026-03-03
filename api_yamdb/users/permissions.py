from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(permissions.BasePermission):
    """Доступ только для модераторов."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Администратор может всё.
    Остальные только читать (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
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
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return (obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)
