from rest_framework import serializers
from core.validators import (
    validate_user_name,
    validate_user_email,
    validate_password_strength,
)
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
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

    def validate_email(self, value):
        return validate_user_email(self.instance, value)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user
