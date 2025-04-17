import re
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import Permission, PermissionGroup, Role, User


class SignUpSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"blank": "Name is required.", "required": "Name is required."}
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "Password is required.",
            "required": "Password is required.",
        },
    )

    class Meta:
        model = User
        fields = ["id", "name", "email", "password"]
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "blank": "Email address is required.",
                    "required": "Email address is required.",
                }
            }
        }

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Name must be at least 3 characters long."
            )

        if len(value) > 50:
            raise serializers.ValidationError("Name cannot exceed 50 characters.")

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(r"[\W_]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid credentials.")

        return {
            "user": user,
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["user_id"] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        role = self.user.role
        grouped_permissions = self.user.get_grouped_permissions()

        data["user"] = {
            "id": self.user.id,
            "name": self.user.name,
            "email": self.user.email,
            "role": role.name if role else None,
            "groupedPermissions": grouped_permissions,
        }

        return data


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "description"]


class PermissionGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = PermissionGroup
        fields = ["id", "name", "description", "permissions"]


class RoleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"blank": "Name is required.", "required": "Name is required."}
    )
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source="permissions",
        error_messages={
            "required": "Permission IDs are required.",
            "does_not_exist": "One or more of the provided permissions could not be found.",
        },
    )
    user_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source="users",
        required=False,
        error_messages={
            "does_not_exist": "One or more of the provided users could not be found.",
        },
    )

    permissions = PermissionSerializer(many=True, read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Role
        fields = ["id", "name", "permission_ids", "user_ids", "permissions", "users"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.context.get("request") and self.context["request"].method in [
            "PUT",
            "PATCH",
        ]:
            self.fields["name"].required = False
            self.fields["permission_ids"].required = False

    def validate_name(self, value):
        if len(value) > 100:
            raise serializers.ValidationError(
                "Name cannot be longer than 100 characters."
            )

        existing_role = (
            Role.objects.filter(name=value)
            .exclude(id=getattr(self.instance, "id", None))
            .exists()
        )
        if existing_role:
            raise serializers.ValidationError("Role with this name already exists.")

        return value

    def get_users(self, obj):
        users = obj.get_users().select_related("role")

        return [
            {"id": user.id, "name": user.name, "email": user.email} for user in users
        ]

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
            User.objects.filter(role=instance).update(role=None)

            for user in users:
                user.role = instance
                user.save()

        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ["id", "name", "email", "role"]
