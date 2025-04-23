import re
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import Permission, PermissionGroup, Role, User

def validate_password_strength(password):
    if len(password) < 8:
        raise serializers.ValidationError(
            "Password must be at least 8 characters long."
        )
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError(
            "Password must contain at least one uppercase letter."
        )
    if not re.search(r"[0-9]", password):
        raise serializers.ValidationError(
            "Password must contain at least one number."
        )
    if not re.search(r"[\W_]", password): 
        raise serializers.ValidationError(
            "Password must contain at least one special character."
        )
    return password

class SignUpSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={"blank": "Name is required.", "required": "Name is required."}
    )
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password_strength],
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

    # Password validation moved to reusable function validate_password_strength

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
            "groupedPermissions",
            "users",
        ]

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

    def get_groupedPermissions(self, obj):
        return obj.get_grouped_permissions()

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

class SimpleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    role = SimpleRoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "role"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', write_only=True, required=False, allow_null=True
    )
    role = SimpleRoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "role_id", "role", "password"] 
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False}
        }

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        if len(value) > 50:
            raise serializers.ValidationError("Name cannot exceed 50 characters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        generated_password = get_random_string(12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)')

        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=generated_password,
            role=validated_data.get('role') 
        )

        self.instance = user 
        self._validated_data['password'] = generated_password
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'password' in self._validated_data:
             representation['password'] = self._validated_data['password']
        return representation


class UserUpdateSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', write_only=True, required=False, allow_null=True
    )
    role = SimpleRoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "role_id", "role", "is_active"]
        read_only_fields = ["id"]
        extra_kwargs = {
            'name': {'required': False}, 
            'email': {'required': False}, 
            'is_active': {'required': False}
        }

    def validate_name(self, value):
        if value is not None: 
            if len(value) < 3:
                raise serializers.ValidationError("Name must be at least 3 characters long.")
            if len(value) > 50:
                raise serializers.ValidationError("Name cannot exceed 50 characters.")
        return value

    def validate_email(self, value):
        if value is not None: 
            if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("User with this email already exists.")
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        if 'role' in validated_data:
             instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance


class UserSetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password_strength],
        error_messages={
            "blank": "Password is required.",
            "required": "Password is required.",
        }
    )

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password_strength] 
    )
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your old password was entered incorrectly. Please enter it again.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "The two password fields didn't match."})
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as the old password."})
        return data
