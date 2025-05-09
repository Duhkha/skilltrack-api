from rest_framework import serializers
from ..models import Expectation, Level

class ExpectationSerializer(serializers.ModelSerializer):
    level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        source='level',
        error_messages={
            "does_not_exist": "Specified level does not exist.",
            "required": "Level is required."
        }
    )
    
    description = serializers.CharField(
        error_messages={
            "blank": "Expectation description is required.",
            "required": "Expectation description is required."
        }
    )
    
    class Meta:
        model = Expectation
        fields = ["id", "level_id", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate_description(self, value):
        value = value.strip()
        
        if not value:
            raise serializers.ValidationError("Expectation description is required.")
            
        if len(value) < 5:
            raise serializers.ValidationError("Expectation description must be at least 5 characters long.")
            
        return value
    
    def create(self, validated_data):
        return Expectation.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance