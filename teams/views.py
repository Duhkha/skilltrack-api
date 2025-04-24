from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from .models import Team
from .serializers import TeamSerializer, TeamDetailSerializer
from accounts.permissions import HasPermission
from accounts.models import User

class TeamPagination(PageNumberPagination):
    page_size = 1 # for testing purposes, set to 1 to see pagination in action
    page_size_query_param = 'page_size'
    max_page_size = 50

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    pagination_class = TeamPagination

    def get_permissions(self):
        """
        Return the appropriate permissions for each action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated(), HasPermission(permission="view_team")]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated(), HasPermission(permission="create_team")]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated(), HasPermission(permission="update_team")]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated(), HasPermission(permission="delete_team")]
        elif self.action in ['add_member', 'remove_member']:
            permission_classes = [permissions.IsAuthenticated(), HasPermission(permission="manage_team_members")]
        else:
            permission_classes = [permissions.IsAuthenticated()]
        
        return permission_classes  
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamDetailSerializer
        return TeamSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a team with specified team lead and members by IDs"""
        data = request.data.copy()
        
        # Get team_lead from ID - require this value
        team_lead_id = data.get('team_lead_id')
        if not team_lead_id:
            return Response({'detail': 'Team lead ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            team_lead = User.objects.get(id=team_lead_id)
            data['team_lead'] = team_lead.id
        except User.DoesNotExist:
            return Response({'detail': 'Team lead user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Handle members data separately
        member_ids = data.pop('members', [])
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save(team_lead=team_lead)
        
        # Add members if provided
        if member_ids:
            existing_members = User.objects.filter(id__in=member_ids)
            team.members.add(*existing_members)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin can see all teams
        if user.is_superuser:
            pass
        # Users with view_team permission can see their teams
        elif HasPermission(permission="view_team").has_permission(self.request, self):
            queryset = queryset.filter(
                Q(members=user) | Q(team_lead=user)
            ).distinct()
        # Others can only see teams they lead
        else:
            queryset = queryset.filter(team_lead=user)
        
        # Filter by search term if provided
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
            
        return queryset

    def check_team_management_permission(self, team):
        """Check if user has permission to manage this specific team"""
        user = self.request.user
        
        return (user.is_superuser or 
                team.team_lead == user or 
                (HasPermission(permission="manage_team_members").has_permission(self.request, self) and 
                 user in team.members.all()))

    @action(detail=True, methods=['post'], url_path='members/add/(?P<user_id>[^/.]+)')
    def add_member(self, request, pk=None, user_id=None):
        """Add a user to the team"""
        team = self.get_object()
        
        if not self.check_team_management_permission(team):
            return Response(
                {'detail': 'You do not have permission to manage this team'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            user = User.objects.get(id=user_id)
            
            if user in team.members.all():
                return Response(
                    {'detail': f'User {user.name} is already a member of this team'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            team.members.add(user)
            return Response({'detail': f'User {user.name} added to team'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'], url_path='members/remove/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        """Remove a user from the team"""
        team = self.get_object()
        
        if not self.check_team_management_permission(team):
            return Response(
                {'detail': 'You do not have permission to manage this team'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            user = User.objects.get(id=user_id)
            
            if user == team.team_lead:
                return Response(
                    {'detail': 'Cannot remove team lead from team'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if user not in team.members.all():
                return Response(
                    {'detail': f'User {user.name} is not a member of this team'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            team.members.remove(user)
            return Response(
                {'detail': f'User {user.name} removed from team'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)