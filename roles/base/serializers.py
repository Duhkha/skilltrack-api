from rest_framework import serializers
from permissions.models import Permission
from core.validators import validate_role_name
from roles.models import Role
from users.models import User


class SimpleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class RoleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"blank": "Name is required.", "required": "Name is required."},
    )
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.get_all(),
        write_only=True,
        source="permissions",
        error_messages={
            "required": "Permission IDs are required.",
            "does_not_exist": "One or more of the provided permissions could not be found.",
        },
    )
    user_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.get_all(),
        write_only=True,
        source="users",
        required=False,
        error_messages={
            "does_not_exist": "One or more of the provided users could not be found.",
        },
    )

    groupedPermissions = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "permission_ids",
            "user_ids",
            "users",
            "groupedPermissions",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.context.get("request") and self.context["request"].method in [
            "PUT",
            "PATCH",
        ]:
            self.fields["name"].required = False
            self.fields["permission_ids"].required = False

    def get_users(self, obj):
        return [
            {"id": user.id, "name": user.name, "email": user.email}
            for user in User.get_by_role(obj)
        ]

    def get_groupedPermissions(self, obj):
        return obj.get_grouped_permissions()

    def validate_name(self, value):
        return validate_role_name(self.instance, value)

    def create(self, validated_data):
        permissions = validated_data.pop("permissions", [])
        users = validated_data.pop("users", [])

        role = Role.objects.create(**validated_data)

        role.permissions.set(permissions)

        for user in users:
            user.role = role
            user.save()

        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop("permissions", None)
        users = validated_data.pop("users", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if permissions is not None:
            instance.permissions.set(permissions)

        if users is not None:
            User.get_by_role(instance).update(role=None)

            for user in users:
                user.role = instance
                user.save()

        instance.save()

        return instance
