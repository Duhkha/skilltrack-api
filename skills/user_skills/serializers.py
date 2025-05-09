from rest_framework import serializers
from ..models import UserSkill, Skill, Level
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSkillSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user',
        error_messages={
            "does_not_exist": "Specified user does not exist.",
            "required": "User is required."
        }
    )
    
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        error_messages={
            "does_not_exist": "Specified skill does not exist.",
            "required": "Skill is required."
        }
    )
    
    current_level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        source='current_level',
        error_messages={
            "does_not_exist": "Specified level does not exist.",
            "required": "Level is required."
        }
    )
    
    # Add read-only fields for nested objects
    user_name = serializers.CharField(source='user.username', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    level_name = serializers.CharField(source='current_level.name', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = ["id", "user_id", "user_name", "skill_id", "skill_name", 
                 "current_level_id", "level_name", "started_at", "updated_at"]
        read_only_fields = ["id", "started_at", "updated_at", "user_name", "skill_name", "level_name"]
    
    def validate(self, data):
        # Ensure the level belongs to the skill
        if 'current_level' in data and 'skill' in data:
            level = data['current_level']
            skill = data['skill']
            
            if level.skill.id != skill.id:
                raise serializers.ValidationError(
                    {"current_level_id": f"The selected level does not belong to the selected skill."}
                )
                
        return data
    
    def create(self, validated_data):
        return UserSkill.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance