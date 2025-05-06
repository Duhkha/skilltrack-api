from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from roles.models import Role


class SignInTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "name": "User",
            "email": "user@example.com",
            "password": "User123!",
        }

        self.view_role = Role.objects.create(name="viewer")
        self.user = User.objects.create_user(
            name=self.user_data["name"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            role=self.view_role,
        )

        self.sign_in_url = reverse("sign-in")

    def test_email_blank(self):
        """
        Test that the email cannot be blank.
        """
        response = self.client.post(
            self.sign_in_url,
            {"email": "", "password": self.user_data["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Email address is required.")

    def test_email_required(self):
        """
        Test that the email is required.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Email address is required.")

    def test_email_whitespace(self):
        """
        Test that leading/trailing whitespace in the email is stripped.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": f"  {self.user_data["email"]}  ",
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)
        self.assertIn("id", response.data["user"])
        self.assertIn("name", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertEqual(response.data["user"]["name"], self.user.name)
        self.assertEqual(response.data["user"]["email"], self.user.email)
        self.assertIn("role", response.data["user"])
        self.assertIn("groupedPermissions", response.data["user"])

    def test_email_case_insensitive(self):
        """
        Test that email is case-insensitive.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": self.user_data["email"].upper(),
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)
        self.assertIn("id", response.data["user"])
        self.assertIn("name", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertEqual(response.data["user"]["name"], self.user.name)
        self.assertEqual(response.data["user"]["email"], self.user.email)
        self.assertIn("role", response.data["user"])
        self.assertIn("groupedPermissions", response.data["user"])

    def test_email_format(self):
        """
        Test that the email follows a valid email format.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": self.user_data["email"].replace(".com", ""),
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Enter a valid email address.")

    def test_password_blank(self):
        """
        Test that the password cannot be blank.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": self.user_data["email"],
                "password": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password is required.")

    def test_password_required(self):
        """
        Test that the password is required.
        """
        response = self.client.post(
            self.sign_in_url, {"email": self.user_data["email"]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password is required.")

    def test_email_invalid_credentials(self):
        """
        Test that the email is invalid, whereas the password is.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": f"invalid_email_{self.user_data["email"]}",
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid credentials.")

    def test_password_invalid_credentials(self):
        """
        Test that the password is invalid, whereas the email is.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": self.user_data["email"],
                "password": f"invalid_password_{self.user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid credentials.")

    def test_valid_credentials(self):
        """
        Test that a user can successfully sign in with valid data.
        """
        response = self.client.post(
            self.sign_in_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)
        self.assertIn("id", response.data["user"])
        self.assertIn("name", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertEqual(response.data["user"]["name"], self.user.name)
        self.assertEqual(response.data["user"]["email"], self.user.email)
        self.assertIn("role", response.data["user"])
        self.assertIn("groupedPermissions", response.data["user"])
