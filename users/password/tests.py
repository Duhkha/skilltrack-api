import re
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from roles.models import Role
from permissions.models import Permission, PermissionGroup


class UserPasswordTests(APITestCase):
    def setUp(self):
        self.users_permission_group = PermissionGroup.objects.create(
            name="users", description="Permissions related to user management."
        )
        self.update_user_permission = Permission.objects.create(
            name="update_user",
            description="Permission to update an existing user.",
            group=self.users_permission_group,
        )

        self.update_role = Role.objects.create(name="updater")
        self.update_role.permissions.set([self.update_user_permission])

        self.update_user_data = {
            "name": "Updater",
            "email": "updater@example.com",
            "password": "Updater123!",
        }
        self.no_role_user_data = {
            "name": "No Role",
            "email": "norole@example.com",
            "password": "NoRole123!",
        }
        self.new_user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "NewUser123!",
        }

        self.update_user = User.objects.create_user(
            name=self.update_user_data["name"],
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
            role=self.update_role,
        )
        self.no_role_user = User.objects.create_user(
            name=self.no_role_user_data["name"],
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )

        self.sign_in_url = reverse("sign-in")
        self.change_password_url = lambda user_id: reverse(
            "user-password-change-password", args=[user_id]
        )
        self.set_password_url = lambda user_id: reverse(
            "user-password-set-password", args=[user_id]
        )

    def authenticate(self, email, password):
        response = self.client.post(
            self.sign_in_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_change_password_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to change password.
        """
        url = self.change_password_url(self.update_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.update_user_data["password"],
                "new_password": f"New{self.update_user_data["password"]}",
                "confirm_new_password": f"New{self.update_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_self(self):
        """
        Test that authenticated users can change their own password.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": f"New{self.no_role_user_data["password"]}",
                "confirm_new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password changed successfully.")

    def test_change_password_no_old(self):
        """
        Test that authenticated users get an appropriate error response when not providing the old password.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": f"New{self.no_role_user_data["password"]}",
                "confirm_new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)
        self.assertEqual(
            response.data["old_password"][0],
            "Old password is required.",
        )

    def test_change_password_no_confirmation(self):
        """
        Test that authenticated users get an appropriate error response when not providing the confirmation password.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_new_password", response.data)
        self.assertEqual(
            response.data["confirm_new_password"][0],
            "Confirmation password is required.",
        )

    def test_change_password_incorrect_old(self):
        """
        Test that authenticated users get an appropriate error response when providing an incorrect old password.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": f"WrongOld{self.no_role_user_data["password"]}",
                "new_password": f"New{self.no_role_user_data["password"]}",
                "confirm_new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)
        self.assertEqual(
            response.data["old_password"][0],
            "Incorrect old password.",
        )

    def test_change_password_mismatch(self):
        """
        Test that authenticated users get an appropriate error response when the new password and confirmation do not match.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": f"New{self.no_role_user_data["password"]}",
                "confirm_new_password": f"New{self.no_role_user_data["password"]}Mismatch",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_new_password", response.data)
        self.assertEqual(
            response.data["confirm_new_password"][0],
            "New password and confirmation do not match.",
        )

    def test_change_password_other_user(self):
        """
        Test that authenticated users cannot change another user's password.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": f"New{self.no_role_user_data["password"]}",
                "confirm_new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to change password of another user.",
        )

    def test_change_password_clears_temp_password(self):
        """
        Test that authenticated users who were manually created (did not do a signup themselves) changing their password clears the temporary plaintext password that was generated when they were created.
        """
        new_user = User.objects.create_user(
            name=self.new_user_data["name"],
            email=self.new_user_data["email"],
            password=self.new_user_data["password"],
            is_manually_created=True,
            temp_plaintext_password=self.new_user_data["password"],
        )
        self.authenticate(
            email=self.new_user_data["email"], password=self.new_user_data["password"]
        )
        url = self.change_password_url(new_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.new_user_data["password"],
                "new_password": f"New{self.new_user_data["password"]}",
                "confirm_new_password": f"New{self.new_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_user.refresh_from_db()
        self.assertIsNone(new_user.temp_plaintext_password)

    def test_set_password_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to set password.
        """
        url = self.set_password_url(self.update_user.id)
        response = self.client.post(
            url,
            {
                "new_password": f"New{self.update_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_password_self(self):
        """
        Test that authenticated users can set their own password.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "Use the change password endpoint to update your own password.",
        )

    def test_set_password_no_permission(self):
        """
        Test that authenticated users who do not have update_user permission cannot set password for other users.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.set_password_url(self.update_user.id)
        response = self.client.post(
            url,
            {
                "new_password": self.update_user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to set password for another user.",
        )

    def test_set_password_old_and_confirmation(self):
        """
        Test that authenticated users who have updater_user permission cannot set password by providing old_password or confirm_new_password.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": f"New{self.no_role_user_data["password"]}",
                "confirm_new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "Do not provide old or confirm password when setting password for another user.",
        )

    def test_set_password(self):
        """
        Test that authenticated users who have update_user permission can set password for other users.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password has been set successfully.")

    def test_set_password_clears_temp_password(self):
        """
        Test that authenticated users that set a password for those that were manually created (did not do a signup themselves) clears the temporary plaintext password that was generated when they were created.
        """
        new_user = User.objects.create_user(
            name=self.new_user_data["name"],
            email=self.new_user_data["email"],
            password=self.new_user_data["password"],
            is_manually_created=True,
            temp_plaintext_password=self.new_user_data["password"],
        )
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(new_user.id)
        response = self.client.post(
            url,
            {
                "new_password": f"New{self.new_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_user.refresh_from_db()
        self.assertIsNone(new_user.temp_plaintext_password)

    def test_set_password_user_not_found(self):
        """
        Test that authenticated users get an appropriate error response when trying to set password for a user that is not found.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(99999)
        response = self.client.post(
            url,
            {"new_password": self.new_user_data["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "User not found.")

    def test_new_password_blank(self):
        """
        Test that the new_password cannot be blank.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": "",
                "confirm_new_password": f"New{self.no_role_user_data["password"]}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(response.data["new_password"][0], "New password is required.")
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(response.data["new_password"][0], "New password is required.")

    def test_new_password_min_length(self):
        """
        Test that the new_password must be at least 8 characters long.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": self.no_role_user_data["password"][:2],
                "confirm_new_password": self.no_role_user_data["password"][:2],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must be at least 8 characters long.",
        )
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": self.no_role_user_data["password"][:2],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must be at least 8 characters long.",
        )

    def test_new_password_uppercase(self):
        """
        Test that the new_password must contain at least one uppercase letter.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": self.no_role_user_data["password"].lower(),
                "confirm_new_password": self.no_role_user_data["password"].lower(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must contain at least one uppercase letter.",
        )
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": self.no_role_user_data["password"].lower(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must contain at least one uppercase letter.",
        )

    def test_new_password_number(self):
        """
        Test that the new_password must contain at least one number.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": f"New{re.sub(r"\d", "", self.no_role_user_data["password"])}",
                "confirm_new_password": f"New{re.sub(r"\d", "", self.no_role_user_data["password"])}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must contain at least one number.",
        )
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": f"New{re.sub(r"\d", "", self.no_role_user_data["password"])}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must contain at least one number.",
        )

    def test_new_password_special_char(self):
        """
        Test that the new_password must contain at least one special character.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        url = self.change_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "old_password": self.no_role_user_data["password"],
                "new_password": re.sub(
                    r"[^a-zA-Z0-9]", "", self.no_role_user_data["password"]
                ),
                "confirm_new_password": re.sub(
                    r"[^a-zA-Z0-9]", "", self.no_role_user_data["password"]
                ),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must contain at least one special character.",
        )
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        url = self.set_password_url(self.no_role_user.id)
        response = self.client.post(
            url,
            {
                "new_password": re.sub(
                    r"[^a-zA-Z0-9]", "", self.no_role_user_data["password"]
                ),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(
            response.data["new_password"][0],
            "New password must contain at least one special character.",
        )
