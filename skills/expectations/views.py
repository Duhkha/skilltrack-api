from django.db import models
from django.http import Http404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from ..models import Expectation
from .serializers import ExpectationSerializer


class ExpectationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class ExpectationViewSet(viewsets.ModelViewSet):
    queryset = Expectation.objects.all()
    serializer_class = ExpectationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ExpectationPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["description"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]
    
    def get_object(self):
        try:
            expectation = super().get_object()
            return expectation
        except Http404:
            raise NotFound("Expectation not found.")
    
    def get_queryset(self):
        if self.kwargs.get('level_pk'):
            return Expectation.objects.filter(level_id=self.kwargs['level_pk']).order_by("created_at")
        return Expectation.objects.all().order_by("created_at")
    
    def list(self, request, *args, **kwargs):
        requesting_user = request.user
        has_view_expectation_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="view_expectation").exists()
        )
        
        if not has_view_expectation_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to view expectations."},
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
            expectation = self.get_object()
            
            requesting_user = request.user
            has_view_expectation_permission = (
                requesting_user.role and requesting_user.role.permissions.filter(name="view_expectation").exists()
            )
            
            if not has_view_expectation_permission and not requesting_user.is_superuser:
                return Response(
                    {"detail": "You do not have permission to view expectations."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = self.get_serializer(expectation)
            return Response(serializer.data)
            
        except NotFound:
            return Response(
                {"detail": "Expectation not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_create_expectation_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="create_expectation").exists()
        )
        
        if not has_create_expectation_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to create expectations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If created within a level, ensure the level_id is set
        if 'level_pk' in self.kwargs:
            request.data['level_id'] = self.kwargs['level_pk']
            
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_update_expectation_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="update_expectation").exists()
        )
        
        if not has_update_expectation_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to update expectations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop("partial", False)
        expectation = self.get_object()
        serializer = self.get_serializer(expectation, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        requesting_user = request.user
        
        has_delete_expectation_permission = (
            requesting_user.role and requesting_user.role.permissions.filter(name="delete_expectation").exists()
        )
        
        if not has_delete_expectation_permission and not requesting_user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete expectations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            expectation = self.get_object()
            expectation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": "Expectation not found."},
                status=status.HTTP_404_NOT_FOUND
            )