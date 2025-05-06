from rest_framework import serializers
from core.validators import validate_password_strength


class UserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "New password is required.",
            "required": "New password is required.",
        },
    )
    confirm_new_password = serializers.CharField(write_only=True, required=False)

    def validate_new_password(self, value):
        return validate_password_strength(value, field_name="New password")

    def validate(self, data):
        user = self.context["request"].user
        is_self = user.id == self.instance.id

        if is_self:
            if not data.get("old_password"):
                raise serializers.ValidationError(
                    {"old_password": "Old password is required."}
                )
            if not data.get("confirm_new_password"):
                raise serializers.ValidationError(
                    {"confirm_new_password": "Confirmation password is required."}
                )
            if not user.check_password(data["old_password"]):
                raise serializers.ValidationError(
                    {"old_password": "Incorrect old password."}
                )
            if data["new_password"] != data["confirm_new_password"]:
                raise serializers.ValidationError(
                    {
                        "confirm_new_password": "New password and confirmation do not match."
                    }
                )
        else:
            if "old_password" in data or "confirm_new_password" in data:
                raise serializers.ValidationError(
                    "Do not provide old or confirm password when setting password for another user."
                )

        return data

    def save(self):
        user = self.instance
        user.set_password(self.validated_data["new_password"])
        user.save()

        if user.is_manually_created and user.temp_plaintext_password is not None:
            user.temp_plaintext_password = None
            user.save()

        return user
