from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from roles.base.serializers import SimpleRoleSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["user_id"] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        role = self.user.role
        if role:
            grouped_permissions = self.user.role.get_grouped_permissions()
        else:
            grouped_permissions = []

        role_data = SimpleRoleSerializer(role).data if role else None

        data["user"] = {
            "id": self.user.id,
            "name": self.user.name,
            "email": self.user.email,
            "role": role_data,
            "groupedPermissions": grouped_permissions,
        }

        return data
