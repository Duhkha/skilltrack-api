from django.conf import settings
from django.http import Http404
from rest_framework import generics, status, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.models import Permission, PermissionGroup, Role, User
from accounts.serializers import (
    CustomTokenObtainPairSerializer,
    SignInSerializer,
    SignUpSerializer,
    PermissionGroupSerializer,
    PermissionSerializer,
    RoleSerializer,
)
from accounts.permissions import HasPermission


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication, BasicAuthentication]


class SignInView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = SignInSerializer(data=request.data)

        if serializer.is_valid():
            token_serializer = CustomTokenObtainPairSerializer(data=request.data)

            if token_serializer.is_valid():
                data = token_serializer.validated_data
                access_token = data["access"]
                refresh_token = data["refresh"]

                response = Response(data, status=status.HTTP_200_OK)

                response.set_cookie(
                    key="accessToken",
                    value=access_token,
                    expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                    secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                )

                response.set_cookie(
                    key="refreshToken",
                    value=refresh_token,
                    expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                    secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                )

                return response
            else:
                return Response(
                    token_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get("refreshToken")
            refresh_token_obj = RefreshToken(refresh_token)

            user_id = refresh_token_obj["user_id"]
            user = User.objects.get(id=user_id)

            refresh_token_obj.blacklist()

            new_refresh_token_obj = RefreshToken.for_user(user)
            new_access_token_obj = new_refresh_token_obj.access_token

            new_refresh_token = str(new_refresh_token_obj)
            new_access_token = str(new_access_token_obj)

            response = Response(
                {"access": new_access_token, "refresh": new_refresh_token},
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="accessToken",
                value=new_access_token,
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )

            response.set_cookie(
                key="refreshToken",
                value=new_refresh_token,
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )

            return response

        except Exception as e:
            raise AuthenticationFailed("Authentication failed.")


class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        grouped_permissions = user.get_grouped_permissions()

        return Response(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.name if user.role else None,
                "grouped-permissions": grouped_permissions,
            }
        )


class SignOutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refreshToken")

        response = Response(
            {"detail": "Successfully signed out."}, status=status.HTTP_200_OK
        )

        response.delete_cookie("accessToken")
        response.delete_cookie("refreshToken")

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return response


class PermissionGroupListView(generics.ListAPIView):
    queryset = PermissionGroup.objects.all()
    serializer_class = PermissionGroupSerializer
    permission_classes = [IsAuthenticated]


class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]


class PermissionListByGroupView(generics.ListAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs.get("group_id")
        group = PermissionGroup.get_by_id(group_id)

        if not group:
            raise NotFound("Permission group not found.")

        return group.get_permissions()


class PermissionDetailView(generics.RetrieveAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        permission_id = self.kwargs.get("permission_id")
        permission = Permission.get_by_id(permission_id)

        if not permission:
            raise NotFound("Permission not found.")

        return permission


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = []

        if self.action == "list":
            permissions = [HasPermission(permission="view_role")]
        elif self.action == "retrieve":
            permissions = [IsAuthenticated()]
        elif self.action == "create":
            permissions = [HasPermission(permission="create_role")]
        elif self.action in ["update", "partial_update"]:
            permissions = [HasPermission(permission="update_role")]
        elif self.action == "destroy":
            permissions = [HasPermission(permission="delete_role")]

        return permissions

    def get_object(self):
        try:
            role = super().get_object()

            return role
        except Http404:
            raise NotFound(detail="Role not found.")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()

        if not hasattr(request.user, "role") or request.user.role is None:
            raise PermissionDenied("User has no assigned role.")

        has_view_permission = request.user.has_permission("view_role")
        is_own_role = request.user.role.id == role.id

        if not has_view_permission and not is_own_role:
            raise PermissionDenied()

        serializer = self.get_serializer(role)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()

            return Response(self.get_serializer(role).data, status=201)

        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        role = self.get_object()

        is_own_role = hasattr(request.user, "role") and request.user.role.id == role.id
        if is_own_role:
            raise PermissionDenied()

        serializer = self.get_serializer(role, data=request.data, partial=False)
        if serializer.is_valid():
            role = serializer.save()

            return Response(self.get_serializer(role).data)

        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()

        is_own_role = hasattr(request.user, "role") and request.user.role.id == role.id
        if is_own_role:
            raise PermissionDenied()

        role.delete()
        return Response({"detail": "Role deleted successfully."}, status=204)
