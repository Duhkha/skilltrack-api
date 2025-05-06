from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from core.utils import normalize_string


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "blank": "Email address is required.",
            "required": "Email address is required.",
        }
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "Password is required.",
            "required": "Password is required.",
        },
    )

    def validate(self, data):
        email = normalize_string(data.get("email"))
        password = data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid credentials.")

        return {"email": user.email, "password": password}
