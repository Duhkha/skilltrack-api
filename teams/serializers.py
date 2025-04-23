from rest_framework import serializers
from .models import Team
from accounts.serializers import UserSerializer

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'team_lead', 'members', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TeamDetailSerializer(TeamSerializer):
    team_lead = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)