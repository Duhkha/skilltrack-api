from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from accounts.models import User


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("accessToken")

        if not token:
            return None

        try:
            access_token = AccessToken(token)

            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)

            return (user, access_token)

        except Exception as e:
            raise AuthenticationFailed("Authentication failed.")

    def authenticate_header(self, request):
        return 'Cookie realm="accessToken"'
