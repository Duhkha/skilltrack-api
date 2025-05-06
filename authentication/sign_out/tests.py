from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from users.models import User


class SignOutTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "name": "User",
            "email": "user@example.com",
            "password": "User123!",
        }

        self.user = User.objects.create_user(
            name=self.user_data["name"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

        self.refresh_token = RefreshToken.for_user(self.user)

        self.sign_out_url = reverse("sign-out")

    def test_no_refresh_token(self):
        """
        Test the sign out when there is no refresh token in the request.
        """
        response = self.client.post(self.sign_out_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Refresh token not provided.")

    def test_invalid_refresh_token(self):
        """
        Test the sign out when the refresh token is invalid.
        """
        self.client.cookies.load({"refreshToken": "invalid_token"})
        response = self.client.post(self.sign_out_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Token is invalid")

    def test_sign_out_success(self):
        """
        Test successful sign out.
        """
        self.client.cookies.load({"refreshToken": self.refresh_token})
        self.client.cookies.load({"accessToken": self.refresh_token.access_token})
        response = self.client.post(self.sign_out_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "You have successfully signed out.")
        self.assertEqual(self.client.cookies["refreshToken"].value, "")
        self.assertEqual(self.client.cookies["accessToken"].value, "")
