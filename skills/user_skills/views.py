from django.db import models
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from ..models import UserSkill
from .serializers import UserSkillSerializer


class UserSkillPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class UserSkillViewSet(viewsets.ModelViewSet):
    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserSkillPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "skill__name"]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]
    
    def get_object(self):
        try:
            user_skill = super().get_object()
            return user_skill
        except Http404:
            raise NotFound("User skill not found.")
    
    def get_queryset(self):
        queryset = UserSkill.objects.all()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by skill if specified
        skill_id = self.request.query_params.get('skill_id', None)
        if skill_id:
            queryset = queryset.filter(skill_id=skill_id)
            
        # Get current user's skills if requested 
        if self.request.query_params.get('my_skills', None) == 'true':
            queryset = queryset.filter(user=self.request.user)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        requesting_user = request.user
        has_view_user_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="view_user_skill").exists()
        )
        
        # Allow users to view their own skills without special permission
        my_skills_only = request.query_params.get('my_skills', None) == 'true'
        
        if not my_skills_only and not has_view_user_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to view user skills."},
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
            user_skill = self.get_object()
            
            requesting_user = request.user
            has_view_user_skill_permission = (
                requesting_user.role and requesting_user.role.permissions.filter(name="view_user_skill").exists()
            )
            
            # Allow users to view their own skills without special permission
            is_own_skill = user_skill.user.id == requesting_user.id
            
            if not is_own_skill and not has_view_user_skill_permission and not requesting_user.is_superuser:
                return Response(
                    {"detail": "You do not have permission to view this user skill."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = self.get_serializer(user_skill)
            return Response(serializer.data)
            
        except NotFound:
            return Response(
                {"detail": "User skill not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_create_user_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="create_user_skill").exists()
        )
        
        if not has_create_user_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to assign skills to users."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_update_user_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="update_user_skill").exists()
        )
        
        if not has_update_user_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to update user skills."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop("partial", False)
        user_skill = self.get_object()
        serializer = self.get_serializer(user_skill, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_delete_user_skill_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="delete_user_skill").exists()
        )
        
        if not has_delete_user_skill_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to remove skills from users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user_skill = self.get_object()
            user_skill.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": "User skill not found."},
                status=status.HTTP_404_NOT_FOUND
            )