from django.db import models
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from ..models import Skill
from .serializers import SkillSerializer


class SkillPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SkillPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "description"]
    ordering = ["name"]
    
    def get_object(self):
        try:
            skill = super().get_object()
            return skill
        except Http404:
            raise NotFound("Skill not found.")
    
    def get_queryset(self):
        queryset = Skill.objects.all().order_by("name")
        
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        requesting_user = request.user
        has_view_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="view_skill").exists()
        )
        
        if not has_view_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to view skills."},
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
            skill = self.get_object()
            
            requesting_user = request.user
            has_view_skill_permission = (
                requesting_user.role and requesting_user.role.permissions.filter(name="view_skill").exists()
            )
            
            if not has_view_skill_permission and not requesting_user.is_superuser:
                return Response(
                    {"detail": "You do not have permission to view skills."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = self.get_serializer(skill)
            return Response(serializer.data)
            
        except NotFound:
            return Response(
                {"detail": "Skill not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_create_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="create_skill").exists()
        )
        
        if not has_create_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to create skills."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_update_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="update_skill").exists()
        )
        
        if not has_update_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to update skills."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop("partial", False)
        skill = self.get_object()
        serializer = self.get_serializer(skill, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_delete_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="delete_skill").exists()
        )
        
        if not has_delete_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete skills."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            skill = self.get_object()
            skill.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": "Skill not found."},
                status=status.HTTP_404_NOT_FOUND
            )