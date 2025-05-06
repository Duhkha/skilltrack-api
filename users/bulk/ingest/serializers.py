from rest_framework import serializers
from core.utils import generate_password
from core.validators import (
    validate_user_name,
)
from roles.base.serializers import SimpleRoleSerializer
from roles.models import Role
from users.models import User


class UserBulkIngestSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[validate_user_name],
        error_messages={"blank": "Name is required.", "required": "Name is required."},
    )
    email = serializers.EmailField(
        error_messages={
            "blank": "Email address is required.",
            "required": "Email address is required.",
        },
    )
    role = serializers.CharField(required=False)
    password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "role", "password"]
        read_only_fields = ["id"]

    def validate_role(self, value):
        try:
            role = Role.objects.get(name=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError(f"Role {value} not found.")

        has_superusers = User.superuser_exists_in_role(role)

        if has_superusers:
            raise serializers.ValidationError(f"Role {value} is a superuser role.")

        return role

    def save(self):
        validated_data = self.validated_data
        name = validated_data["name"]
        email = validated_data["email"]
        role = validated_data.get("role")

        user = User.get_by_email(email).first()
        self.context["operation"] = "update" if user else "create"

        if user:
            user.name = name
            user.email = email
            user.role = role
            user.save()
        else:
            generated_password = generate_password()

            user = User.objects.create_user(
                name=name,
                email=email,
                role=role,
                password=generated_password,
                is_manually_created=True,
            )
            user.temp_plaintext_password = generated_password
            user.save(update_fields=["temp_plaintext_password"])

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        requesting_user = request.user if request else None

        if not request:
            return representation

        if instance.role:
            representation["role"] = SimpleRoleSerializer(instance.role).data

        operation = self.context.get("operation", None)

        if operation == "update":
            representation.pop("password", None)
        else:
            has_import_user_permission = (
                requesting_user.role
                and requesting_user.role.has_permission("create_user")
                and requesting_user.role.has_permission("update_user")
            )
            if has_import_user_permission and instance.is_manually_created:
                if instance.temp_plaintext_password:
                    representation["password"] = instance.temp_plaintext_password
            else:
                representation.pop("password", None)

        return representation
