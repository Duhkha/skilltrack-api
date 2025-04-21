from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    def __init__(self, permission):
        self.permission = permission

    def has_permission(self, request, view):
        user = request.user

        if user.is_authenticated:
            if user.has_permission(self.permission):
                return True
        return False
