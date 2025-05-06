import re
from rest_framework import serializers
from core.utils import normalize_string
from roles.models import Role
from users.models import User


def validate_user_name(name):
    name = name.strip()

    if len(name) < 3:
        raise serializers.ValidationError("Name must be at least 3 characters long.")

    if len(name) > 50:
        raise serializers.ValidationError("Name cannot exceed 50 characters.")

    return name


def validate_user_email(instance, email):
    email = normalize_string(email)

    existing_email = (
        User.get_by_email(email).exclude(id=getattr(instance, "id", None)).exists()
    )
    if existing_email:
        raise serializers.ValidationError("User with this email already exists.")

    return email


def validate_role_name(instance, name):
    name = name.strip()

    if len(name) > 100:
        raise serializers.ValidationError("Name cannot be longer than 100 characters.")

    existing_role = (
        Role.get_by_name(name).exclude(id=getattr(instance, "id", None)).exists()
    )
    if existing_role:
        raise serializers.ValidationError("Role with this name already exists.")

    return name


def validate_password_strength(password, field_name="Password"):
    if len(password) < 8:
        raise serializers.ValidationError(
            f"{field_name} must be at least 8 characters long."
        )

    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError(
            f"{field_name} must contain at least one uppercase letter."
        )

    if not re.search(r"[0-9]", password):
        raise serializers.ValidationError(
            f"{field_name} must contain at least one number."
        )

    if not re.search(r"[\W_]", password):
        raise serializers.ValidationError(
            f"{field_name} must contain at least one special character."
        )

    return password
