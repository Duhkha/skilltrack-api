from rest_framework import serializers
from ..models import UserExpectationProgress, Expectation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserExpectationProgressSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user',
        error_messages={
            "does_not_exist": "Specified user does not exist.",
            "required": "User is required."
        }
    )
    
    expectation_id = serializers.PrimaryKeyRelatedField(
        queryset=Expectation.objects.all(),
        source='expectation',
        error_messages={
            "does_not_exist": "Specified expectation does not exist.",
            "required": "Expectation is required."
        }
    )
    
    # Add read-only fields for nested objects
    user_name = serializers.CharField(source='user.username', read_only=True)
    expectation_description = serializers.CharField(source='expectation.description', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = UserExpectationProgress
        fields = ["id", "user_id", "user_name", "expectation_id", "expectation_description", 
                 "status", "notes", "updated_at", "approved_at", "approved_by", "approved_by_name"]
        read_only_fields = ["id", "updated_at", "approved_at", "user_name", 
                          "expectation_description", "approved_by_name"]
    
    def validate_status(self, value):
        valid_statuses = [status[0] for status in UserExpectationProgress.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def create(self, validated_data):
        return UserExpectationProgress.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        # Special handling for status changes to 'approved'
        if 'status' in validated_data and validated_data['status'] == 'approved':
            # Only admins or users with approve permission can set status to approved
            user = self.context['request'].user
            has_approve_permission = (
                user.role and user.role.permissions.filter(name="approve_expectation").exists() or
                user.is_superuser
            )
            
            if not has_approve_permission:
                raise serializers.ValidationError(
                    {"status": "You do not have permission to approve expectations."}
                )
                
            # Set approved_by and approved_at
            from django.utils import timezone
            validated_data['approved_by'] = user
            validated_data['approved_at'] = timezone.now()
            
        # Regular update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance