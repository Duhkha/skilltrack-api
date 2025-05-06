from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from permissions.models import Permission
from roles.models import Role
from users.models import User
from roles.base.serializers import RoleSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.get_all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def check_all_permissions_role_exists(self):
        return Role.get_roles_with_all_permissions().exists()

    def get_object(self):
        try:
            role = super().get_object()

            return role
        except Http404:
            raise NotFound("Role not found.")

    def list(self, request):
        requesting_user = request.user
        search = request.query_params.get("search", "").strip().lower()
        queryset = self.get_queryset()

        if requesting_user.is_superuser:
            queryset = queryset.filter(name__icontains=search)
        else:
            has_view_role_permission = (
                requesting_user.role
                and requesting_user.role.has_permission("view_role")
            )

            if has_view_role_permission:
                superuser_ids = User.get_superusers().values_list("id", flat=True)

                queryset = queryset.exclude(user__id__in=superuser_ids).filter(
                    name__icontains=search
                )
            else:
                if (
                    hasattr(requesting_user, "role")
                    and requesting_user.role is not None
                ):
                    queryset = Role.get_by_id(requesting_user.role.id)
                else:
                    queryset = Role.objects.none()

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        requesting_user = request.user
        role = self.get_object()

        if requesting_user.is_superuser:
            serializer = self.get_serializer(role)

            return Response(serializer.data)

        if not hasattr(requesting_user, "role") or requesting_user.role is None:
            raise PermissionDenied("User has no assigned role.")

        has_view_role_permission = (
            requesting_user.role and requesting_user.role.has_permission("view_role")
        )
        is_own_role = requesting_user.role.id == role.id
        if not has_view_role_permission and not is_own_role:
            raise PermissionDenied("You do not have permission to view this role.")

        has_superusers = User.superuser_exists_in_role(role)
        if has_superusers:
            raise PermissionDenied("You cannot view a superuser role.")

        serializer = self.get_serializer(role)

        return Response(serializer.data)

    def create(self, request):
        requesting_user = request.user
        user_ids = request.data.get("user_ids")

        has_create_role_permission = (
            requesting_user.role and requesting_user.role.has_permission("create_role")
        )

        if not has_create_role_permission:
            raise PermissionDenied("You do not have permission to create a role.")

        if user_ids:
            if str(requesting_user.id) in map(str, user_ids):
                raise PermissionDenied("You cannot assign roles to yourself.")

            superuser_ids = list(
                User.get_superusers_in_ids(user_ids).values_list("id", flat=True)
            )
            if superuser_ids:
                raise PermissionDenied("You cannot assign roles to superusers.")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()

            all_permissions_count = Permission.count_all()
            has_all_permissions = role.permissions.count() == all_permissions_count

            if has_all_permissions and self.check_all_permissions_role_exists():
                raise PermissionDenied("A role with all permissions already exists.")

            if has_all_permissions and user_ids:
                User.get_by_ids(user_ids).update(is_staff=True, is_superuser=True)

            return Response(
                self.get_serializer(role).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        role = self.get_object()

        has_update_role_permission = (
            requesting_user.role and requesting_user.role.has_permission("update_role")
        )

        if not has_update_role_permission:
            raise PermissionDenied("You do not have permission to update this role.")

        is_own_role = (
            hasattr(requesting_user, "role") and requesting_user.role.id == role.id
        )
        if is_own_role:
            raise PermissionDenied("You cannot update your own role.")

        has_superusers = User.superuser_exists_in_role(role)
        if has_superusers:
            raise PermissionDenied("You cannot update a superuser role.")

        user_ids = request.data.get("user_ids")
        if user_ids:
            if str(requesting_user.id) in map(str, user_ids):
                raise PermissionDenied("You cannot assign roles to yourself.")

            superuser_ids = list(
                User.get_superusers_in_ids(user_ids).values_list("id", flat=True)
            )
            if superuser_ids:
                raise PermissionDenied("You cannot assign roles to superusers.")

        serializer = self.get_serializer(role, data=request.data, partial=False)
        if serializer.is_valid():
            role = serializer.save()

            all_permissions_count = Permission.count_all()
            has_all_permissions = role.permissions.count() == all_permissions_count

            if has_all_permissions and self.check_all_permissions_role_exists():
                raise PermissionDenied("A role with all permissions already exists.")

            if has_all_permissions:
                if user_ids:
                    User.get_by_ids(user_ids).update(is_staff=True, is_superuser=True)
                else:
                    User.get_by_role(role).update(is_staff=True, is_superuser=True)

            return Response(
                self.get_serializer(role).data,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        role = self.get_object()

        has_delete_role_permission = (
            requesting_user.role and requesting_user.role.has_permission("delete_role")
        )

        if not has_delete_role_permission:
            raise PermissionDenied("You do not have permission to delete this role.")

        is_own_role = (
            hasattr(requesting_user, "role") and requesting_user.role.id == role.id
        )
        if is_own_role:
            raise PermissionDenied("You cannot delete your own role.")

        has_superusers = User.superuser_exists_in_role(role)
        if has_superusers:
            raise PermissionDenied("You cannot delete a superuser role.")

        role.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
