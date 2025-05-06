from rest_framework import serializers
from permissions.models import PermissionGroup
from permissions.base.serializers import PermissionSerializer


class PermissionGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = PermissionGroup
        fields = ["id", "name", "description", "permissions"]
