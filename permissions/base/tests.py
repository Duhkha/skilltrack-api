from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from permissions.models import PermissionGroup
from users.models import User


class PermissionTests(APITestCase):
    def setUp(self):
        self.roles_permission_group_data = {
            "name": "roles",
            "description": "Permissions related to role management.",
        }
        self.users_permission_group_data = {
            "name": "users",
            "description": "Permissions related to user management.",
        }
        self.view_role_permission_data = {
            "name": "view_role",
            "description": "Permission to view roles, including listing all roles and retrieving individual role details.",
        }
        self.create_role_permission_data = {
            "name": "create_role",
            "description": "Permission to create a new role.",
        }
        self.update_role_permission_data = {
            "name": "update_role",
            "description": "Permission to update an existing role.",
        }
        self.delete_role_permission_data = {
            "name": "delete_role",
            "description": "Permission to delete a role.",
        }
        self.view_user_permission_data = {
            "name": "view_user",
            "description": "Permission to view users, including listing all users and retrieving individual user details.",
        }
        self.create_user_permission_data = {
            "name": "create_user",
            "description": "Permission to create a new user.",
        }
        self.update_user_permission_data = {
            "name": "update_user",
            "description": "Permission to update an existing user.",
        }
        self.delete_user_permission_data = {
            "name": "delete_user",
            "description": "Permission to delete a user.",
        }
        self.user_data = {
            "name": "User",
            "email": "user@example.com",
            "password": "User123!",
        }

        self.roles_permission_group = PermissionGroup.objects.create(
            name=self.roles_permission_group_data["name"],
            description=self.roles_permission_group_data["description"],
        )
        self.users_permission_group = PermissionGroup.objects.create(
            name=self.users_permission_group_data["name"],
            description=self.users_permission_group_data["description"],
        )

        self.view_role_permission = self.roles_permission_group.permissions.create(
            name=self.view_role_permission_data["name"],
            description=self.view_role_permission_data["description"],
        )
        for name, description in [
            (
                self.create_role_permission_data["name"],
                self.create_role_permission_data["description"],
            ),
            (
                self.update_role_permission_data["name"],
                self.update_role_permission_data["description"],
            ),
            (
                self.delete_role_permission_data["name"],
                self.delete_role_permission_data["description"],
            ),
        ]:
            self.roles_permission_group.permissions.create(
                name=name, description=description
            )

        for name, description in [
            (
                self.view_user_permission_data["name"],
                self.view_user_permission_data["description"],
            ),
            (
                self.create_user_permission_data["name"],
                self.create_user_permission_data["description"],
            ),
            (
                self.update_user_permission_data["name"],
                self.update_user_permission_data["description"],
            ),
            (
                self.delete_user_permission_data["name"],
                self.delete_user_permission_data["description"],
            ),
        ]:
            self.users_permission_group.permissions.create(
                name=name, description=description
            )

        self.user = User.objects.create_user(
            name=self.user_data["name"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

        self.sign_in_url = reverse("sign-in")
        self.permissions_url = reverse("permissions-list")
        self.permission_url = lambda permission_id: reverse(
            "permissions-detail", args=[permission_id]
        )

    def authenticate(self):
        response = self.client.post(
            self.sign_in_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to permissions.
        """
        response = self.client.get(self.permissions_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permissions(self):
        """
        Test that authenticated users can get permissions.
        """
        self.authenticate()
        response = self.client.get(self.permissions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)
        permission_names = [permission["name"] for permission in response.data]
        self.assertEqual(
            set(permission_names),
            {
                self.view_role_permission_data["name"],
                self.create_role_permission_data["name"],
                self.update_role_permission_data["name"],
                self.delete_role_permission_data["name"],
                self.view_user_permission_data["name"],
                self.create_user_permission_data["name"],
                self.update_user_permission_data["name"],
                self.delete_user_permission_data["name"],
            },
        )

    def test_permissions_search_by_permission_name(self):
        """
        Test that authenticated users can search permissions by a permission name.
        """
        self.authenticate()
        response = self.client.get(
            self.permissions_url, {"search": self.view_role_permission_data["name"]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("description", response.data[0])
        self.assertEqual(response.data[0]["id"], self.view_role_permission.id)
        self.assertEqual(response.data[0]["name"], self.view_role_permission.name)
        self.assertEqual(
            response.data[0]["description"],
            self.view_role_permission.description,
        )

    def test_permissions_search_no_results(self):
        """
        Test that authenticated users searching permissions by a non-existent permission name get no results.
        """
        self.authenticate()
        response = self.client.get(
            self.permissions_url,
            {"search": f"non_existent_{self.view_role_permission_data["name"]}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_permission_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to a permission.
        """
        response = self.client.get(self.permission_url(self.view_role_permission.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permission(self):
        """
        Test that authenticated users can get a permission.
        """
        self.authenticate()
        response = self.client.get(self.permission_url(self.view_role_permission.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("description", response.data)
        self.assertEqual(response.data["id"], self.view_role_permission.id)
        self.assertEqual(response.data["name"], self.view_role_permission.name)
        self.assertEqual(
            response.data["description"],
            self.view_role_permission.description,
        )

    def test_permission_not_found(self):
        """
        Test that authenticated users retrieving a non-existent permission get an appropriate error response.
        """
        self.authenticate()
        response = self.client.get(self.permission_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
