from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.models import User
from accounts.serializers import (
    SignUpSerializer,
    SignInSerializer,
    CustomTokenObtainPairSerializer,
)


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

        return Response({"name": user.name, "email": user.email})


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
