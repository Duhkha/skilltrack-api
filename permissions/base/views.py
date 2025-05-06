from django.http import Http404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from permissions.models import Permission
from permissions.base.serializers import PermissionSerializer


class PermissionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.get_all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            permission = super().get_object()

            return permission
        except Http404:
            raise NotFound("Permission not found.")

    def list(self, request):
        search = request.query_params.get("search", "").strip().lower()
        queryset = self.get_queryset()

        if search:
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        permission = self.get_object()
        serializer = self.get_serializer(permission)

        return Response(serializer.data)
