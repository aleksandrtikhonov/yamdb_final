from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Кастмоный пермишен для Category, Genre, Title.
    POST/DELETE запросы доступны только администратору и суперюзеру.
    PUT запрос запрещен.
    """
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return request.user.is_admin_or_superuser

    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT':
            return False
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return request.user.is_admin_or_superuser


class IsAdmin(permissions.BasePermission):
    """
    Доступ только администратору.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin_or_superuser


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    """Доступ на изменение автору, админу, модератору"""
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin_or_superuser
                or request.user.is_moderator)
