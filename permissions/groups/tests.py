from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from permissions.models import PermissionGroup
from users.models import User


class PermissionGroupTests(APITestCase):
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

        for name, description in [
            (
                self.view_role_permission_data["name"],
                self.view_role_permission_data["description"],
            ),
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

        self.view_user_permission = self.users_permission_group.permissions.create(
            name=self.view_user_permission_data["name"],
            description=self.view_user_permission_data["description"],
        )
        for name, description in [
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
        self.permission_groups_url = reverse("permission-groups-list")
        self.permission_group_url = lambda group_id: reverse(
            "permission-groups-detail", args=[group_id]
        )
        self.permission_group_permissions_url = lambda group_id: reverse(
            "permission-groups-permissions", args=[group_id]
        )

    def authenticate(self):
        response = self.client.post(
            self.sign_in_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permission_groups_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to permission groups.
        """
        response = self.client.get(self.permission_groups_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permission_groups(self):
        """
        Test that authenticated users can get permission groups.
        """
        self.authenticate()
        response = self.client.get(self.permission_groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group_names = [group["name"] for group in response.data]
        self.assertIn(self.roles_permission_group_data["name"], group_names)
        self.assertIn(self.users_permission_group_data["name"], group_names)

    def test_permission_groups_search_by_group_name(self):
        """
        Test that authenticated users can search permission groups by their group name.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_groups_url,
            {"search": self.users_permission_group_data["name"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("description", response.data[0])
        self.assertIn("permissions", response.data[0])
        self.assertEqual(len(response.data[0]["permissions"]), 4)
        self.assertEqual(response.data[0]["id"], self.users_permission_group.id)
        self.assertEqual(response.data[0]["name"], self.users_permission_group.name)
        self.assertEqual(
            response.data[0]["description"], self.users_permission_group.description
        )
        permission_names = [
            permission["name"] for permission in response.data[0]["permissions"]
        ]
        self.assertEqual(
            set(permission_names),
            {
                self.view_user_permission_data["name"],
                self.create_user_permission_data["name"],
                self.update_user_permission_data["name"],
                self.delete_user_permission_data["name"],
            },
        )

    def test_permission_groups_search_by_permission_name(self):
        """
        Test that authenticated users can search permission groups by a permission name.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_groups_url,
            {"search": self.view_user_permission_data["name"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("description", response.data[0])
        self.assertIn("permissions", response.data[0])
        self.assertEqual(len(response.data[0]["permissions"]), 1)
        self.assertEqual(response.data[0]["id"], self.users_permission_group.id)
        self.assertEqual(response.data[0]["name"], self.users_permission_group.name)
        self.assertEqual(
            response.data[0]["description"], self.users_permission_group.description
        )
        self.assertIn("id", response.data[0]["permissions"][0])
        self.assertIn("name", response.data[0]["permissions"][0])
        self.assertIn("description", response.data[0]["permissions"][0])
        self.assertEqual(
            response.data[0]["permissions"][0]["id"], self.view_user_permission.id
        )
        self.assertEqual(
            response.data[0]["permissions"][0]["name"],
            self.view_user_permission.name,
        )
        self.assertEqual(
            response.data[0]["permissions"][0]["description"],
            self.view_user_permission.description,
        )

    def test_permission_groups_search_no_results(self):
        """
        Test that authenticated users searching permission groups by a non-existent group or permission name get no results.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_groups_url, {"search": "non_existent"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_permission_group_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to a permission group.
        """
        response = self.client.get(
            self.permission_group_url(self.roles_permission_group.id)
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permission_group(self):
        """
        Test that authenticated users can get a permission group.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_group_url(self.roles_permission_group.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("description", response.data)
        self.assertEqual(response.data["id"], self.roles_permission_group.id)
        self.assertEqual(response.data["name"], self.roles_permission_group.name)
        self.assertEqual(
            response.data["description"],
            self.roles_permission_group.description,
        )

    def test_permission_group_not_found(self):
        """
        Test that authenticated users retrieving a non-existent permission group get an appropriate error response.
        """
        self.authenticate()
        response = self.client.get(self.permission_group_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_permission_group_permissions_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to permissions in a permission group.
        """
        response = self.client.get(
            self.permission_group_permissions_url(self.roles_permission_group.id)
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_roles_permission_group_permissions(self):
        """
        Test that authenticated users can get all permissions for the roles permission group.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_group_permissions_url(self.roles_permission_group.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        permission_names = [permission["name"] for permission in response.data]
        self.assertEqual(
            set(permission_names),
            {
                self.view_role_permission_data["name"],
                self.create_role_permission_data["name"],
                self.update_role_permission_data["name"],
                self.delete_role_permission_data["name"],
            },
        )

    def test_users_permission_group_permissions(self):
        """
        Test that authenticated users can get all permissions for the users permission group.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_group_permissions_url(self.users_permission_group.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        permission_names = [permission["name"] for permission in response.data]
        self.assertEqual(
            set(permission_names),
            {
                self.view_user_permission_data["name"],
                self.create_user_permission_data["name"],
                self.update_user_permission_data["name"],
                self.delete_user_permission_data["name"],
            },
        )

    def test_permission_group_permissions_search_by_permission_name(self):
        """
        Test that authenticated users can search permissions in a permission group by permission name.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_group_permissions_url(self.users_permission_group.id),
            {"search": self.view_user_permission_data["name"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("description", response.data[0])
        self.assertEqual(response.data[0]["id"], self.view_user_permission.id)
        self.assertEqual(response.data[0]["name"], self.view_user_permission.name)
        self.assertEqual(
            response.data[0]["description"],
            self.view_user_permission.description,
        )

    def test_permission_group_permissions_search_no_results(self):
        """
        Test that authenticated users searching permissions in a permission group by non-existent permission name get no results.
        """
        self.authenticate()
        response = self.client.get(
            self.permission_group_permissions_url(self.users_permission_group.id),
            {"search": "non_existent"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_permission_group_permissions_not_found(self):
        """
        Test that authenticated users retrieving permissions for a non-existent permission group get an appropriate error response.
        """
        self.authenticate()
        response = self.client.get(self.permission_group_permissions_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
