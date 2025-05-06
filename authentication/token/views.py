from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class CustomTokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
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
