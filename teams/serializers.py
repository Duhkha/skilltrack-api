from rest_framework import serializers
from .models import Team
from accounts.models import User
from accounts.serializers import UserSerializer
from collections import Counter

class SimpleUserSerializer(serializers.ModelSerializer):
    """A lightweight serializer for User objects in team responses"""
    class Meta:
        model = User
        fields = ['id', 'name']

class TeamSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        error_messages={
            "blank": "Team name is required.",
            "required": "Team name is required."
        }
    )
    team_lead_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='team_lead',
        write_only=True,
        required=False,
        allow_null=True,
        error_messages={
            "does_not_exist": "The specified team lead does not exist."
        }
    )
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='members',
        required=False,
        error_messages={
            "does_not_exist": "One or more of the specified members do not exist."
        }
    )
    team_lead = SimpleUserSerializer(read_only=True)
    members = SimpleUserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'team_lead_id', 'team_lead', 'member_ids', 'members', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Team name must be at least 3 characters long.")
        
        # Check for uniqueness, excluding current instance when updating
        existing_team = (
            Team.objects.filter(name=value)
            .exclude(id=getattr(self.instance, "id", None))
            .exists()
        )
        if existing_team:
            raise serializers.ValidationError("Team with this name already exists.")
            
        return value
    
    def validate_member_ids(self, members):
        """Validate that there are no duplicate members in the request"""
        member_counts = Counter(member.id for member in members)
        duplicates = [member_id for member_id, count in member_counts.items() if count > 1]
        
        if duplicates:
            duplicate_names = [User.objects.get(id=user_id).name for user_id in duplicates]
            raise serializers.ValidationError(
                f"Duplicate members found: {', '.join(duplicate_names)}. Each user can only be added once."
            )
        
        return members
    
    def validate(self, data):
        """Validate that the team lead is not also included as a member"""
        team_lead = data.get('team_lead')
        members = data.get('members', [])
        
        if team_lead and team_lead in members:
            raise serializers.ValidationError({
                "member_ids": f"The team lead ({team_lead.name}) should not be included in the members list."
            })
        
        return data
    
    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        team = Team.objects.create(**validated_data)
        
        if members_data:
            team.members.set(members_data)
            
        return team
    
    def update(self, instance, validated_data):
        members_data = validated_data.pop('members', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if members_data is not None:
            instance.members.set(members_data)
            
        instance.save()
        return instance


class TeamDetailSerializer(serializers.ModelSerializer):
    team_lead = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'team_lead', 'members', 
                  'member_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()