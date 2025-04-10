import re
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import User


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

        data["user"] = {
            "name": self.user.name,
            "email": self.user.email,
        }

        return data
