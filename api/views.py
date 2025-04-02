from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken 

class HealthCheckView(APIView):
    """ A simple view to check if the API service is running. """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok", "message": "API is running"}, status=status.HTTP_200_OK)

class CustomLoginView(APIView):
    """ Temporary, hardcoded login """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    HARDCODED_USERNAME = "testuser"
    HARDCODED_PASSWORD = "testpassword123" 

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if username == self.HARDCODED_USERNAME and password == self.HARDCODED_PASSWORD:
            print("Hardcoded credentials match. Generating tokens.")
            refresh = RefreshToken.for_user(DummyUser())
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': { 'username': self.HARDCODED_USERNAME } 
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            print("Hardcoded credentials mismatch.")
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class DummyUser:
    id = 1 