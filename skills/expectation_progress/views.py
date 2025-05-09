from django.db import models
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action

from ..models import UserExpectationProgress, Expectation, Level, UserSkill
from .serializers import UserExpectationProgressSerializer
from django.utils import timezone


class ExpectationProgressPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class UserExpectationProgressViewSet(viewsets.ModelViewSet):
    queryset = UserExpectationProgress.objects.all()
    serializer_class = UserExpectationProgressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ExpectationProgressPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["expectation__description", "notes"]
    ordering_fields = ["updated_at", "status"]
    ordering = ["-updated_at"]
    
    def get_object(self):
        try:
            progress = super().get_object()
            return progress
        except Http404:
            raise NotFound("Progress record not found.")
    
    def get_queryset(self):
        queryset = UserExpectationProgress.objects.all()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by expectation if specified
        expectation_id = self.request.query_params.get('expectation_id', None)
        if expectation_id:
            queryset = queryset.filter(expectation_id=expectation_id)
        
        # Filter by level if specified
        level_id = self.request.query_params.get('level_id', None)
        if level_id:
            queryset = queryset.filter(expectation__level_id=level_id)
        
        # Filter by skill if specified
        skill_id = self.request.query_params.get('skill_id', None)
        if skill_id:
            queryset = queryset.filter(expectation__level__skill_id=skill_id)
            
        # Filter by status if specified
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Get current user's progress if requested 
        if self.request.query_params.get('my_progress', None) == 'true':
            queryset = queryset.filter(user=self.request.user)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        requesting_user = request.user
        has_view_progress_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="view_expectation_progress").exists()
        )
        
        # Allow users to view their own progress without special permission
        my_progress_only = request.query_params.get('my_progress', None) == 'true'
        
        if not my_progress_only and not has_view_progress_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to view progress records."},
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
            progress = self.get_object()
            
            requesting_user = request.user
            has_view_progress_permission = (
                requesting_user.role and requesting_user.role.permissions.filter(name="view_expectation_progress").exists()
            )
            
            # Allow users to view their own progress without special permission
            is_own_progress = progress.user.id == requesting_user.id
            
            if not is_own_progress and not has_view_progress_permission and not requesting_user.is_superuser:
                return Response(
                    {"detail": "You do not have permission to view this progress record."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = self.get_serializer(progress)
            return Response(serializer.data)
            
        except NotFound:
            return Response(
                {"detail": "Progress record not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_create_progress_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="create_expectation_progress").exists()
        )
        
        if not has_create_progress_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to create progress records."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        progress = self.get_object()
        
        has_update_progress_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="update_expectation_progress").exists()
        )
        
        # Allow users to update their own progress from 'not_started' to 'completed'
        is_own_progress = progress.user.id == requesting_user.id
        is_valid_status_change = (
            is_own_progress and
            progress.status == 'not_started' and
            request.data.get('status') == 'completed'
        )
        
        if not is_valid_status_change and not has_update_progress_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to update this progress record."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(progress, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_delete_progress_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="delete_expectation_progress").exists()
        )
        
        if not has_delete_progress_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete progress records."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            progress = self.get_object()
            progress.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": "Progress record not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def approve_and_advance(self, request):
        """
        Approve all completed expectations for a user's skill and advance them to the next level
        """
        requesting_user = request.user
        has_approve_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="approve_expectation").exists()
        )
        
        if not has_approve_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to approve expectations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        skill_id = request.data.get('skill_id')
        
        if not user_id or not skill_id:
            return Response(
                {"detail": "Both user_id and skill_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get the user's current skill level
            user_skill = UserSkill.objects.get(user_id=user_id, skill_id=skill_id)
            current_level = user_skill.current_level
            
            # Get all expectations for this level
            level_expectations = Expectation.objects.filter(level=current_level)
            
            # Get the user's progress on these expectations
            progress_records = UserExpectationProgress.objects.filter(
                user_id=user_id,
                expectation__in=level_expectations
            )
            
            # Check if all expectations are at least completed
            incomplete_expectations = progress_records.filter(
                status__in=['not_started']
            ).count()
            
            if incomplete_expectations > 0:
                return Response(
                    {"detail": "Not all expectations are completed. Cannot advance level."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Approve all completed expectations
            now = timezone.now()
            completed_records = progress_records.filter(status='completed')
            for record in completed_records:
                record.status = 'approved'
                record.approved_by = requesting_user
                record.approved_at = now
                record.save()
                
            # Find the next level for this skill
            try:
                next_level = Level.objects.get(
                    skill_id=skill_id,
                    order=current_level.order + 1
                )
                
                # Update the user's skill level
                user_skill.current_level = next_level
                user_skill.save()
                
                # Create 'not_started' progress records for the new level's expectations
                next_level_expectations = Expectation.objects.filter(level=next_level)
                for expectation in next_level_expectations:
                    UserExpectationProgress.objects.create(
                        user_id=user_id,
                        expectation=expectation,
                        status='not_started'
                    )
                
                return Response({
                    "detail": "All expectations approved and user advanced to next level.",
                    "new_level": next_level.name,
                    "new_level_id": next_level.id
                })
                
            except Level.DoesNotExist:
                return Response({
                    "detail": "All expectations approved. User has reached maximum level for this skill.",
                    "new_level": current_level.name,
                    "new_level_id": current_level.id
                })
                
        except UserSkill.DoesNotExist:
            return Response(
                {"detail": "User does not have the specified skill assigned."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )