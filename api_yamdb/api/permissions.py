from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'admin' or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return getattr(request.user, 'role', None) == 'admin' or request.user.is_superuser
