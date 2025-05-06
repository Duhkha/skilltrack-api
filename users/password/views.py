from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from users.models import User
from users.password.serializers import UserPasswordSerializer


class UserPasswordViewSet(viewsets.GenericViewSet):
    queryset = User.objects.select_related("role").all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            user = super().get_object()

            return user
        except Http404:
            raise NotFound("User not found.")

    def _handle_password_update(self, request, user, success_message):
        serializer = UserPasswordSerializer(
            user, data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response({"detail": success_message}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post"],
        url_path="password/change",
    )
    def change_password(self, request, *args, **kwargs):
        requesting_user = request.user
        target_user = self.get_object()

        is_self = requesting_user.id == target_user.id

        if not is_self:
            raise PermissionDenied(
                "You do not have permission to change password of another user."
            )

        return self._handle_password_update(
            request, target_user, success_message="Password changed successfully."
        )

    @action(detail=True, methods=["post"], url_path="password/set")
    def set_password(self, request, *args, **kwargs):
        requesting_user = request.user
        target_user = self.get_object()

        is_self = request.user.id == target_user.id

        if is_self:
            raise PermissionDenied(
                "Use the change password endpoint to update your own password."
            )

        has_update_permission = (
            requesting_user.role and requesting_user.role.has_permission("update_user")
        )

        if not has_update_permission:
            raise PermissionDenied(
                "You do not have permission to set password for another user."
            )

        return self._handle_password_update(
            request, target_user, success_message="Password has been set successfully."
        )
