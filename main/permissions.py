from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.method in permissions.SAFE_METHODS


class IsCurrentUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'profile'):
            return bool(request.user.profile == obj.profile)
        return bool(request.user.profile_user == obj)


class UserHasProfile(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile_user')
