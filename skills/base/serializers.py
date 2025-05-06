from rest_framework import serializers
from ..models import Skill

class SkillSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        error_messages={
            "blank": "Skill name is required.",
            "required": "Skill name is required.",
            "max_length": "Skill name cannot exceed 100 characters."
        }
    )
    
    class Meta:
        model = Skill
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate_name(self, value):
        value = value.strip()
        
        if not value:
            raise serializers.ValidationError("Skill name is required.")
            
        if len(value) < 2:
            raise serializers.ValidationError("Skill name must be at least 2 characters long.")
        
        if len(value) > 100:
            raise serializers.ValidationError("Skill name cannot exceed 100 characters.")
            
        existing_skill = (
            Skill.objects.filter(name=value)
            .exclude(id=getattr(self.instance, "id", None))
            .exists()
        )
        if existing_skill:
            raise serializers.ValidationError("Skill with this name already exists.")
            
        return value
    
    def create(self, validated_data):
        return Skill.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance