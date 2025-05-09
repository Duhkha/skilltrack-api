from rest_framework import serializers
from ..models import Level, Skill

class LevelSerializer(serializers.ModelSerializer):
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        error_messages={
            "does_not_exist": "Specified skill does not exist.",
            "required": "Skill is required."
        }
    )
    
    name = serializers.CharField(
        max_length=100,
        error_messages={
            "blank": "Level name is required.",
            "required": "Level name is required.",
            "max_length": "Level name cannot exceed 100 characters."
        }
    )
    
    order = serializers.IntegerField(
        error_messages={
            "required": "Level order is required.",
            "invalid": "Level order must be a positive integer."
        }
    )
    
    class Meta:
        model = Level
        fields = ["id", "skill_id", "name", "order", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate_name(self, value):
        value = value.strip()
        
        if not value:
            raise serializers.ValidationError("Level name is required.")
            
        if len(value) < 2:
            raise serializers.ValidationError("Level name must be at least 2 characters long.")
        
        if len(value) > 100:
            raise serializers.ValidationError("Level name cannot exceed 100 characters.")
            
        return value
    
    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError("Level order must be a positive integer.")
        return value
    
    def validate(self, data):
        skill = data.get('skill')
        order = data.get('order')
        
        if skill and order and not self.instance:
            existing_level = Level.objects.filter(skill=skill, order=order).exists()
            if existing_level:
                raise serializers.ValidationError(
                    {"order": f"A level with order {order} already exists for this skill."}
                )
        
        if self.instance and (skill or order):
            updated_skill = skill or self.instance.skill
            updated_order = order or self.instance.order
            
            existing_level = (
                Level.objects.filter(skill=updated_skill, order=updated_order)
                .exclude(id=self.instance.id)
                .exists()
            )
            if existing_level:
                raise serializers.ValidationError(
                    {"order": f"A level with order {updated_order} already exists for this skill."}
                )
                
        return data
    
    def create(self, validated_data):
        return Level.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance