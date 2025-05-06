from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    def __init__(self, permission):
        self.permission = permission

    def has_permission(self, request, view):
        requesting_user = request.user

        if requesting_user.is_authenticated:
            if requesting_user.role and requesting_user.role.has_permission(
                self.permission
            ):
                return True

        return False
