from rest_framework import viewsets, permissions, status
from .models import Team
from .serializers import TeamSerializer, TeamDetailSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from accounts.permissions import HasPermission


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

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
    
    def perform_create(self, serializer):
        serializer.save(team_lead=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin can see all teams
        if user.is_superuser:
            pass
        # Regular users with view_team permission can see all teams they belong to 
        # or teams they lead
        elif HasPermission(permission="view_team").has_permission(self.request, self):
            queryset = queryset.filter(
                Q(members=user) | Q(team_lead=user)
            ).distinct()
        # Users without view_team permission can only see teams they lead
        else:
            queryset = queryset.filter(team_lead=user)
        
        # Filter by search param if provided
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
        
        # Admin can manage any team
        if user.is_superuser:
            return True
        
        # Team lead can always manage their team
        if team.team_lead == user:
            return True
        
        # Users with manage_team_members permission can only manage teams they belong to
        if (HasPermission(permission="manage_team_members").has_permission(self.request, self) and
            user in team.members.all()):
            return True
            
        return False

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a user to the team"""
        team = self.get_object()
        
        # Check if user can manage this team
        if not self.check_team_management_permission(team):
            return Response(
                {'detail': 'You do not have permission to manage this team'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        user_id = request.data.get('user_id')
        
        from accounts.models import User
        try:
            user = User.objects.get(id=user_id)
            
            # Check if user is already a member
            if user in team.members.all():
                return Response(
                    {'detail': f'User {user.name} is already a member of this team'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            team.members.add(user)
            return Response({'detail': f'User {user.name} added to team'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a user from the team"""
        team = self.get_object()
        
        # Check if user can manage this team
        if not self.check_team_management_permission(team):
            return Response(
                {'detail': 'You do not have permission to manage this team'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        user_id = request.data.get('user_id')
        
        from accounts.models import User
        try:
            user = User.objects.get(id=user_id)
            
            # Cannot remove the team lead
            if user == team.team_lead:
                return Response(
                    {'detail': 'Cannot remove team lead from team'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Check if user is actually a member
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