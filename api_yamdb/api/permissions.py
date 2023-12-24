from rest_framework import permissions

from reviews.models import CustomUser


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (getattr(request.user, 'role', None)
                == CustomUser.ADMIN or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (getattr(request.user, 'role', None)
                == CustomUser.ADMIN or request.user.is_superuser)


class IsModeratorIsAdminOrReadonly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.role == CustomUser.ADMIN)


class IsOwnerIsModeratorIsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.role == CustomUser.ADMIN
                or request.user.role == CustomUser.MODERATOR)
