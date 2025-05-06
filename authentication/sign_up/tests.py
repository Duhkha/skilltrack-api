import re
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SignUpTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "name": "User",
            "email": "user@example.com",
            "password": "User123!",
        }

        self.sign_up_url = reverse("sign-up")

    def test_name_blank(self):
        """
        Test that the name cannot be blank.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": "",
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name is required.")

    def test_name_required(self):
        """
        Test that the name is required.
        """
        response = self.client.post(
            self.sign_up_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name is required.")

    def test_name_whitespace(self):
        """
        Test that leading/trailing whitespace in the name is stripped.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": f"  {self.user_data["name"]}  ",
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["name"], self.user_data["name"])
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_name_min_length(self):
        """
        Test that the name must be at least 3 characters long.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"][:2],
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0], "Name must be at least 3 characters long."
        )

    def test_name_max_length(self):
        """
        Test that the name cannot be more than 50 characters long.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"][0] * 51,
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name cannot exceed 50 characters.")

    def test_email_blank(self):
        """
        Test that the email cannot be blank.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": "",
                "password": self.user_data["password"],
            },
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
            self.sign_up_url,
            {
                "name": self.user_data["name"],
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
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": f"  {self.user_data["email"]}  ",
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["name"], self.user_data["name"])
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_email_case_insensitive(self):
        """
        Test that the email is case insensitive.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": self.user_data["email"].upper(),
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["name"], self.user_data["name"])
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_email_format(self):
        """
        Test that the email follows a valid email format.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
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
            self.sign_up_url,
            {
                "name": self.user_data["name"],
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
            self.sign_up_url,
            {"name": self.user_data["name"], "email": self.user_data["email"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password is required.")

    def test_password_min_length(self):
        """
        Test that the password must be at least 8 characters long.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": self.user_data["email"],
                "password": self.user_data["password"][:2],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(
            response.data["password"][0], "Password must be at least 8 characters long."
        )

    def test_password_uppercase(self):
        """
        Test that the password must contain at least one uppercase letter.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": self.user_data["email"],
                "password": self.user_data["password"].lower(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(
            response.data["password"][0],
            "Password must contain at least one uppercase letter.",
        )

    def test_password_number(self):
        """
        Test that the password must contain at least one number.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": self.user_data["email"],
                "password": f"NoNumbers{re.sub(r"\d", "", self.user_data["password"])}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(
            response.data["password"][0], "Password must contain at least one number."
        )

    def test_password_special_char(self):
        """
        Test that the password must contain at least one special character.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": self.user_data["email"],
                "password": f"New{re.sub(
                    r"[^a-zA-Z0-9]", "", self.user_data["password"]
                )}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(
            response.data["password"][0],
            "Password must contain at least one special character.",
        )

    def test_user_exists(self):
        """
        Test that a user cannot sign up with an existing email.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        response = self.client.post(
            self.sign_up_url,
            {
                "name": f"New {self.user_data["name"]}",
                "email": self.user_data["email"],
                "password": f"New{self.user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data["email"][0], "User with this email already exists."
        )

    def test_valid_data(self):
        """
        Test that a user can successfully sign up with valid data.
        """
        response = self.client.post(
            self.sign_up_url,
            {
                "name": self.user_data["name"],
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["name"], self.user_data["name"])
        self.assertEqual(response.data["email"], self.user_data["email"])
