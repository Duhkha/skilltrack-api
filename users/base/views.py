from django.db import models
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from users.models import User
from users.base.serializers import UserSerializer


class CustomUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 15


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("role").all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomUserPagination

    def get_queryset(self):
        requesting_user = self.request.user
        queryset = super().get_queryset()

        if self.action == "list":
            if requesting_user.is_superuser:
                queryset = queryset.exclude(id=requesting_user.id)
            else:
                queryset = queryset.exclude(id=requesting_user.id).exclude(
                    is_superuser=True
                )

        search = self.request.query_params.get("search", "").strip().lower()
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search)
                | models.Q(email__icontains=search)
                | models.Q(role__name__icontains=search)
            )

        ordering = self.request.query_params.get("ordering")
        if ordering:
            ordering_fields = [field.strip() for field in ordering.split(",")]
            queryset = queryset.order_by(*ordering_fields)
        else:
            queryset = queryset.order_by("role", "name")

        return queryset

    def get_object(self):
        try:
            user = super().get_object()

            return user
        except Http404:
            raise NotFound("User not found.")

    def list(self, request):
        requesting_user = request.user

        has_view_user_permission = (
            requesting_user.role and requesting_user.role.has_permission("view_user")
        )
        if not has_view_user_permission:
            raise PermissionDenied("You do not have permission to view users.")

        queryset = self.get_queryset().exclude(id=requesting_user.id)

        if not requesting_user.is_superuser:
            queryset = queryset.exclude(is_superuser=True)

        page_param = request.query_params.get("page")
        page_size_param = request.query_params.get("page_size")

        if page_param and page_size_param:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)

                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        requesting_user = request.user
        target_user = self.get_object()

        is_self = requesting_user.id == target_user.id

        if is_self:
            serializer = self.get_serializer(target_user)

            return Response(serializer.data)

        if requesting_user.is_superuser:
            serializer = self.get_serializer(target_user)

            return Response(serializer.data)

        if target_user.is_superuser:
            raise PermissionDenied("You cannot view a superuser.")

        has_view_user_permission = (
            requesting_user.role and requesting_user.role.has_permission("view_user")
        )

        if not has_view_user_permission:
            raise PermissionDenied("You do not have permission to view this user.")

        serializer = self.get_serializer(target_user)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        requesting_user = request.user

        has_create_user_permission = (
            requesting_user.role and requesting_user.role.has_permission("create_user")
        )

        if not has_create_user_permission:
            raise PermissionDenied("You do not have permission to create a user.")

        serializer_context = self.get_serializer_context()
        serializer_context.update({"operation": "create"})

        serializer = self.get_serializer(data=request.data, context=serializer_context)
        if serializer.is_valid():
            user = serializer.save()

            serialized_user = self.get_serializer(user, context=serializer_context).data

            return Response(
                serialized_user,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        target_user = self.get_object()

        is_self = requesting_user.id == target_user.id

        if not is_self:
            has_update_user_permission = (
                requesting_user.role
                and requesting_user.role.has_permission("update_user")
            )
            if not has_update_user_permission:
                raise PermissionDenied(
                    "You do not have permission to update this user."
                )

            if target_user.is_superuser:
                raise PermissionDenied("You cannot update a superuser.")

        serializer_context = self.get_serializer_context()
        serializer_context.update({"operation": "update"})

        serializer = self.get_serializer(
            target_user, data=request.data, context=serializer_context
        )
        if serializer.is_valid():
            user = serializer.save()

            serialized_user = self.get_serializer(user, context=serializer_context).data

            return Response(serialized_user)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        target_user = self.get_object()

        is_self = requesting_user.id == target_user.id

        if not is_self:
            has_delete_user_permission = (
                requesting_user.role
                and requesting_user.role.has_permission("delete_user")
            )
            if not has_delete_user_permission:
                raise PermissionDenied(
                    "You do not have permission to delete this user."
                )

        if target_user.is_superuser:
            raise PermissionDenied("You cannot delete a superuser.")

        target_user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
