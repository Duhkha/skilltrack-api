from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class AuthTokensTests(APITestCase):
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

        self.sign_in_url = reverse("sign-in")
        self.sign_out_url = reverse("sign-out")
        self.token_refresh_url = reverse("token-refresh")

    def test_no_refresh_token(self):
        """
        Test refresh endpoint when there is no refresh token in the request.
        """
        response = self.client.post(self.token_refresh_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(str(response.data["detail"]), "Authentication failed.")

    def test_invalid_refresh_token(self):
        """
        Test refresh endpoint when the refresh token is invalid.
        """
        self.client.cookies.load({"refreshToken": "invalid_token"})
        response = self.client.post(self.token_refresh_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(str(response.data["detail"]), "Authentication failed.")

    def test_sign_in_and_refresh_token(self):
        """
        Test successful sign in and refresh token flow.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        refresh_token = response.data["refresh"]
        access_token = response.data["access"]
        self.client.cookies.load({"refreshToken": refresh_token})
        self.client.cookies.load({"accessToken": access_token})
        response = self.client.post(self.token_refresh_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refreshToken", response.cookies)
        self.assertIn("accessToken", response.cookies)
        self.assertEqual(
            response.data["refresh"], response.cookies["refreshToken"].value
        )
        self.assertEqual(response.data["access"], response.cookies["accessToken"].value)
        self.assertNotEqual(response.data["refresh"], refresh_token)
        self.assertNotEqual(response.data["access"], access_token)

    def test_blacklisted_token_invalid_after_sign_out(self):
        """
        Test that the token is invalidated after sign-out and cannot be used again.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data["refresh"]
        self.client.cookies.load({"refreshToken": refresh_token})
        self.client.post(self.sign_out_url)
        response = self.client.post(self.token_refresh_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Authentication failed.")
