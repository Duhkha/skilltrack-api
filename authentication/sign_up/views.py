from rest_framework import generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny
from authentication.sign_up.serializers import SignUpSerializer
from users.models import User


class SignUpView(generics.CreateAPIView):
    queryset = User.get_all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
