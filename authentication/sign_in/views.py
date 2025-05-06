from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from authentication.sign_in.serializers import SignInSerializer
from authentication.token.serializers import CustomTokenObtainPairSerializer


class SignInView(TokenObtainPairView):
    def post(self, request):
        serializer = SignInSerializer(data=request.data)

        if serializer.is_valid():
            token_serializer = CustomTokenObtainPairSerializer(
                data=serializer.validated_data
            )

            if token_serializer.is_valid():
                data = token_serializer.validated_data
                access_token = data["access"]
                refresh_token = data["refresh"]

                response = Response(data)

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
