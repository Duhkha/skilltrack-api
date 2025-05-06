from django.db import models
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from ..models import Team
from .serializers import TeamSerializer, TeamDetailSerializer
from users.models import User


class TeamPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TeamPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "description"]
    ordering = ["name"]
    
    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeamDetailSerializer
        return TeamSerializer
    
    def get_object(self):
        try:
            team = super().get_object()
            return team
        except Http404:
            raise NotFound("Team not found.")
    
    def get_queryset(self):
        queryset = Team.objects.all().order_by("name")
        
        # Apply search filtering manually to ensure it works correctly
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        requesting_user = request.user
        has_view_team_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="view_team").exists()
        )
        
        if not has_view_team_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to view teams."},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.filter_queryset(self.get_queryset())
        
        # Use pagination only if specifically requested
        if "page" in request.query_params or "page_size" in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            # First try to get the team - if it doesn't exist, return 404
            team = self.get_object()
            
            # If team exists, check for permissions
            requesting_user = request.user
            has_view_team_permission = (
                requesting_user.role and requesting_user.role.permissions.filter(name="view_team").exists()
            )
            
            if not has_view_team_permission and not requesting_user.is_superuser:
                return Response(
                    {"detail": "You do not have permission to view teams."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = self.get_serializer(team)
            return Response(serializer.data)
            
        except NotFound:
            return Response(
                {"detail": "Team not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_create_team_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="create_team").exists()
        )
        
        if not has_create_team_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to create teams."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        team = self.get_object()
        
        # Allow team leads to update their own teams regardless of permission
        is_team_lead = team.team_lead == requesting_user
        has_update_team_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="update_team").exists()
        )
        
        if not is_team_lead and not has_update_team_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to update teams."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(team, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_delete_team_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="delete_team").exists()
        )
        
        if not has_delete_team_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete teams."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get the team first (this may raise an exception if not found)
            team = self.get_object()
            # Then delete it
            team.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # If there's any error (like team not found), return 404
            return Response(
                {"detail": "Team not found."},
                status=status.HTTP_404_NOT_FOUND
            )