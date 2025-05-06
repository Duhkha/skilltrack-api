from django.http import Http404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from permissions.models import PermissionGroup
from permissions.base.serializers import PermissionSerializer
from permissions.groups.serializers import PermissionGroupSerializer


class PermissionGroupsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PermissionGroupSerializer
    permission_classes = [IsAuthenticated]
    queryset = PermissionGroup.get_all().prefetch_related("permissions")

    def get_object(self):
        try:
            permission_group = super().get_object()

            return permission_group
        except Http404:
            raise NotFound("Permission group not found.")

    def list(self, request):
        search = request.query_params.get("search", "").strip().lower()
        queryset = self.get_queryset()
        result = []

        for group in queryset:
            group_name_match = search and search in group.name.lower()

            matching_permissions = [
                permission
                for permission in group.permissions.all()
                if search in permission.name.lower()
            ]

            if group_name_match:
                serialized = self.get_serializer(group).data

                result.append(serialized)
            elif matching_permissions:
                serialized = self.get_serializer(group).data
                serialized["permissions"] = [
                    {
                        "id": permission.id,
                        "name": permission.name,
                        "description": permission.description,
                    }
                    for permission in matching_permissions
                ]

                result.append(serialized)

        return Response(result)

    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(group)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="permissions",
        permission_classes=[IsAuthenticated],
    )
    def permissions(self, request, *args, **kwargs):
        group = self.get_object()

        search = request.query_params.get("search", "").strip().lower()

        permissions = group.permissions.all()
        if search:
            permissions = permissions.filter(name__icontains=search)

        serializer = PermissionSerializer(permissions, many=True)

        return Response(serializer.data)
