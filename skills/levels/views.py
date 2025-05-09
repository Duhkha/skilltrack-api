from django.db import models
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from ..models import Level
from .serializers import LevelSerializer


class LevelPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LevelPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "description"]
    ordering = ["name"]
    
    def get_object(self):
        try:
            level = super().get_object()
            return level
        except Http404:
            raise NotFound("Level not found.")
    
    def get_queryset(self):
        if self.kwargs.get('skill_pk'):
            return Level.objects.filter(skill_id=self.kwargs['skill_pk']).order_by("name")
        return Level.objects.all().order_by("name")
    
    
    def list(self, request, *args, **kwargs):
        requesting_user = request.user
        has_view_level_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="view_level").exists()
        )
        
        if not has_view_level_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to view levels."},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.filter_queryset(self.get_queryset())
        
        if "page" in request.query_params or "page_size" in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            level = self.get_object()
            
            requesting_user = request.user
            has_view_level_permission = (
                requesting_user.role and requesting_user.role.permissions.filter(name="view_level").exists()
            )
            
            if not has_view_level_permission and not requesting_user.is_superuser:
                return Response(
                    {"detail": "You do not have permission to view levels."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = self.get_serializer(level)
            return Response(serializer.data)
            
        except NotFound:
            return Response(
                {"detail": "Level not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_create_level_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="create_level").exists()
        )
        
        if not has_create_level_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to create levels."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_update_level_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="update_level").exists()
        )
        
        if not has_update_level_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to update levels."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop("partial", False)
        level = self.get_object()
        serializer = self.get_serializer(level, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_delete_level_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="delete_level").exists()
        )
        
        if not has_delete_level_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete levels."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            level = self.get_object()
            level.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": "Level not found."},
                status=status.HTTP_404_NOT_FOUND
            )