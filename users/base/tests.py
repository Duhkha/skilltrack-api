from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from permissions.models import Permission, PermissionGroup
from roles.models import Role
from users.models import User


class UserTests(APITestCase):
    def setUp(self):
        self.roles_permission_group = PermissionGroup.objects.create(
            name="roles", description="Permissions related to role management."
        )
        self.users_permission_group = PermissionGroup.objects.create(
            name="users", description="Permissions related to user management."
        )

        self.view_role_permission = Permission.objects.create(
            name="view_role",
            description="Permission to view roles.",
            group=self.roles_permission_group,
        )
        self.create_role_permission = Permission.objects.create(
            name="create_role",
            description="Permission to create a new role.",
            group=self.roles_permission_group,
        )
        self.update_role_permission = Permission.objects.create(
            name="update_role",
            description="Permission to update an existing role.",
            group=self.roles_permission_group,
        )
        self.delete_role_permission = Permission.objects.create(
            name="delete_role",
            description="Permission to delete a role.",
            group=self.roles_permission_group,
        )
        self.view_user_permission = Permission.objects.create(
            name="view_user",
            description="Permission to view users, including listing all users and retrieving individual user details.",
            group=self.users_permission_group,
        )
        self.create_user_permission = Permission.objects.create(
            name="create_user",
            description="Permission to create a new user.",
            group=self.users_permission_group,
        )
        self.update_user_permission = Permission.objects.create(
            name="update_user",
            description="Permission to update an existing user.",
            group=self.users_permission_group,
        )
        self.delete_user_permission = Permission.objects.create(
            name="delete_user",
            description="Permission to delete a user.",
            group=self.users_permission_group,
        )

        self.admin_role = Role.objects.create(name="admin")
        self.view_role = Role.objects.create(name="viewer")
        self.create_role = Role.objects.create(name="creator")
        self.update_role = Role.objects.create(name="updater")
        self.delete_role = Role.objects.create(name="deleter")

        self.admin_role.permissions.set(
            [
                self.view_role_permission,
                self.create_role_permission,
                self.update_role_permission,
                self.delete_role_permission,
                self.view_user_permission,
                self.create_user_permission,
                self.update_user_permission,
                self.delete_user_permission,
            ]
        )
        self.view_role.permissions.set(
            [self.view_role_permission, self.view_user_permission]
        )
        self.create_role.permissions.set(
            [self.create_role_permission, self.create_user_permission]
        )
        self.update_role.permissions.set(
            [self.update_role_permission, self.update_user_permission]
        )
        self.delete_role.permissions.set(
            [self.delete_role_permission, self.delete_user_permission]
        )

        self.admin_user_data = {
            "name": "Admin",
            "email": "admin@example.com",
            "password": "Admin123!",
        }
        self.view_user_data = {
            "name": "Viewer",
            "email": "viewer@example.com",
            "password": "Viewer123!",
        }
        self.create_user_data = {
            "name": "Creator",
            "email": "creator@example.com",
            "password": "Creator123!",
        }
        self.update_user_data = {
            "name": "Updater",
            "email": "updater@example.com",
            "password": "Updater123!",
        }
        self.delete_user_data = {
            "name": "Deleter",
            "email": "deleter@example.com",
            "password": "Deleter123!",
        }
        self.new_user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "NewUser123!",
        }
        self.superuser_data = {
            "name": "Superuser",
            "email": "superuser@example.com",
            "password": "Superuser123!",
        }

        self.admin_user = User.objects.create_superuser(
            name=self.admin_user_data["name"],
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
            role=self.admin_role,
        )
        self.view_user = User.objects.create_user(
            name=self.view_user_data["name"],
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
            role=self.view_role,
        )
        self.create_user = User.objects.create_user(
            name=self.create_user_data["name"],
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
            role=self.create_role,
        )
        self.update_user = User.objects.create_user(
            name=self.update_user_data["name"],
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
            role=self.update_role,
        )
        self.delete_user = User.objects.create_user(
            name=self.delete_user_data["name"],
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
            role=self.delete_role,
        )

        self.sign_in_url = reverse("sign-in")
        self.users_url = reverse("users-list")
        self.user_url = lambda user_id: reverse("users-detail", args=[user_id])

    def authenticate(self, email, password):
        response = self.client.post(
            self.sign_in_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_users_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to users.
        """
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_no_permission(self):
        """
        Test that authenticated users who do not have view_user permission cannot get users.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to view users.",
        )

    def test_users_superuser(self):
        """
        Test that authenticated users who are superusers can get all users, except themselves.
        """
        self.authenticate(
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
        )
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("email", response.data[0])
        self.assertIn("role", response.data[0])
        self.assertIn("id", response.data[0]["role"])
        self.assertIn("name", response.data[0]["role"])
        self.assertNotIn("password", response.data[0])
        self.assertEqual(response.data[0]["id"], self.view_user.id)
        self.assertEqual(response.data[0]["name"], self.view_user.name)
        self.assertEqual(response.data[0]["email"], self.view_user.email)
        self.assertEqual(response.data[0]["role"]["id"], self.view_user.role.id)
        self.assertEqual(response.data[0]["role"]["name"], self.view_user.role.name)

    def test_users_non_superuser_has_permission(self):
        """
        Test that authenticated users who are not superusers and who have view_user permission
        can get all users, except themselves and superusers.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for user in response.data:
            self.assertNotEqual(user["email"], self.admin_user.email)
            self.assertNotEqual(user["email"], self.view_user.email)

    def test_users_search_by_name(self):
        """
        Test that authenticated users who have view_user permission can search users by name.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.users_url, {"search": self.create_user.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("email", response.data[0])
        self.assertIn("role", response.data[0])
        self.assertIn("id", response.data[0]["role"])
        self.assertIn("name", response.data[0]["role"])
        self.assertNotIn("password", response.data[0])
        self.assertEqual(response.data[0]["id"], self.create_user.id)
        self.assertEqual(response.data[0]["name"], self.create_user.name)
        self.assertEqual(response.data[0]["email"], self.create_user.email)
        self.assertEqual(response.data[0]["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data[0]["role"]["name"], self.create_user.role.name)

    def test_users_search_by_email(self):
        """
        Test that authenticated users who have view_user permission can search users by email.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.users_url, {"search": self.create_user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("email", response.data[0])
        self.assertIn("role", response.data[0])
        self.assertIn("id", response.data[0]["role"])
        self.assertIn("name", response.data[0]["role"])
        self.assertNotIn("password", response.data[0])
        self.assertEqual(response.data[0]["id"], self.create_user.id)
        self.assertEqual(response.data[0]["name"], self.create_user.name)
        self.assertEqual(response.data[0]["email"], self.create_user.email)
        self.assertEqual(response.data[0]["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data[0]["role"]["name"], self.create_user.role.name)

    def test_users_search_by_role(self):
        """
        Test that authenticated users who have view_user permission can search users by role.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(
            self.users_url, {"search": self.create_user.role.name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertIn("email", response.data[0])
        self.assertIn("role", response.data[0])
        self.assertIn("id", response.data[0]["role"])
        self.assertIn("name", response.data[0]["role"])
        self.assertNotIn("password", response.data[0])
        self.assertEqual(response.data[0]["id"], self.create_user.id)
        self.assertEqual(response.data[0]["name"], self.create_user.name)
        self.assertEqual(response.data[0]["email"], self.create_user.email)
        self.assertEqual(response.data[0]["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data[0]["role"]["name"], self.create_user.role.name)

    def test_users_ordering(self):
        """
        Test that authenticated users who have view_user permission can get ordered users by specified fields.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.users_url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [user["name"] for user in response.data]
        sorted_names = sorted(names)
        self.assertEqual(names, sorted_names)
        response = self.client.get(self.users_url, {"ordering": "-name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [user["name"] for user in response.data]
        sorted_names = sorted(names, reverse=True)
        self.assertEqual(names, sorted_names)

    def test_users_pagination(self):
        """
        Test that authenticated users who have view_user permission can get users that are paginated correctly.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.users_url, {"page": 1, "page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    def test_user_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to a user.
        """
        response = self.client.get(self.user_url(self.view_user.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_self(self):
        """
        Test that authenticated users who do not have view_user permission can get their own details.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.get(self.user_url(self.create_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["id"], self.create_user.id)
        self.assertEqual(response.data["name"], self.create_user.name)
        self.assertEqual(response.data["email"], self.create_user.email)
        self.assertEqual(response.data["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data["role"]["name"], self.create_user.role.name)

    def test_user_no_permission(self):
        """
        Test that authenticated users who do not have view_user permission cannot get details of another user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.get(self.user_url(self.view_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to view this user.",
        )

    def test_user_non_superuser_has_permission(self):
        """
        Test that authenticated users who are not superusers and who have view_user permission
        can get details of another user, except superusers.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.user_url(self.create_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["id"], self.create_user.id)
        self.assertEqual(response.data["name"], self.create_user.name)
        self.assertEqual(response.data["email"], self.create_user.email)
        self.assertEqual(response.data["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data["role"]["name"], self.create_user.role.name)
        response = self.client.get(self.user_url(self.admin_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot view a superuser.",
        )

    def test_user_not_found(self):
        """
        Test that authenticated users who have view_user permission retrieving a non-existent user get an appropriate error response.
        """
        self.authenticate(
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
        )
        response = self.client.get(self.user_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "User not found.")

    def test_create_user_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to creating a user.
        """
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_no_permission(self):
        """
        Test that authenticated users who do not have create_user permission cannot create a user.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to create a user.",
        )

    def test_create_user_exists(self):
        """
        Test that authenticated users who have create_user permission cannot create a user with the same email as an existing user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": self.view_user.email,
                "role_id": self.view_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data["email"][0],
            "User with this email already exists.",
        )

    def test_create_user_assign_superuser_role(self):
        """
        Test that authenticated users who have create_user permission cannot create a user with the superuser role.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.superuser_data["name"],
                "email": self.superuser_data["email"],
                "role_id": self.admin_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot assign a superuser role.",
        )

    def test_create_user(self):
        """
        Test that authenticated users who have create_user permission can create a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertIn("password", response.data)
        self.assertEqual(response.data["name"], self.new_user_data["name"])
        self.assertEqual(response.data["email"], self.new_user_data["email"])
        self.assertEqual(response.data["role"]["id"], self.view_role.id)
        self.assertEqual(response.data["role"]["name"], self.view_role.name)
        created_user = User.objects.get(email=self.new_user_data["email"])
        self.assertTrue(created_user.is_manually_created)
        self.assertIsNotNone(created_user.temp_plaintext_password)

    def test_update_user_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to updating a user.
        """
        response = self.client.put(
            self.user_url(self.view_user.id),
            {
                "name": f"Updated {self.view_user.name}",
                "email": self.view_user.email,
                "role_id": self.view_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_self(self):
        """
        Test that authenticated users who do not have update_user permission can update their own details.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.view_user.id),
            {
                "name": f"Updated {self.view_user.name}",
                "email": self.view_user.email,
                "role_id": self.view_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["id"], self.view_user.id)
        self.assertEqual(response.data["name"], f"Updated {self.view_user.name}")
        self.assertEqual(response.data["email"], self.view_user.email)
        self.assertEqual(response.data["role"]["id"], self.view_user.role.id)
        self.assertEqual(response.data["role"]["name"], self.view_user.role.name)

    def test_update_other_user_no_permission(self):
        """
        Test that authenticated users who do not have update_user permission cannot update other users.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": f"Updated {self.create_user.name}",
                "email": self.create_user.email,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to update this user.",
        )

    def test_update_superuser(self):
        """
        Test that authenticated users who have update_user permission cannot update a superuser.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.admin_user.id),
            {
                "name": f"Updated {self.admin_user.name}",
                "email": self.admin_user.email,
                "role_id": self.admin_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot update a superuser.",
        )

    def test_update_user(self):
        """
        Test that authenticated users who have update_user permission can update other users.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": f"Updated {self.create_user.name}",
                "email": self.create_user.email,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["id"], self.create_user.id)
        self.assertEqual(response.data["name"], f"Updated {self.create_user.name}")
        self.assertEqual(response.data["email"], self.create_user.email)
        self.assertEqual(response.data["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data["role"]["name"], self.create_user.role.name)

    def test_update_user_exists(self):
        """
        Test that authenticated users who have update_user permission cannot update a user with the same email as an existing user.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.view_user.id),
            {
                "name": self.view_user.name,
                "email": self.create_user.email,
                "role_id": self.view_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_update_user_not_found(self):
        """
        Test that authenticated users who have view_user permission updating a non-existent user get an appropriate error response.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(99999),
            {
                "name": self.new_user_data["name"],
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "User not found.")

    def test_user_name_blank(self):
        """
        Test that a user cannot be created or updated with a blank name.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": "",
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name is required.")
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": "",
                "email": self.create_user.email,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name is required.")

    def test_user_name_required(self):
        """
        Test that the name is required when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"][0], "Name is required.")
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "email": self.create_user.email,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name is required.")

    def test_user_name_whitespace(self):
        """
        Test that leading/trailing whitespace in the name is stripped when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": f"  {self.new_user_data["name"]}  ",
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertIn("password", response.data)
        self.assertEqual(response.data["name"], self.new_user_data["name"])
        self.assertEqual(response.data["email"], self.new_user_data["email"])
        self.assertEqual(response.data["role"]["id"], self.view_role.id)
        self.assertEqual(response.data["role"]["name"], self.view_role.name)
        created_user = User.objects.get(email=self.new_user_data["email"])
        self.assertTrue(created_user.is_manually_created)
        self.assertIsNotNone(created_user.temp_plaintext_password)
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": f"  Updated {self.create_user.name}  ",
                "email": self.create_user.email,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["id"], self.create_user.id)
        self.assertEqual(response.data["name"], f"Updated {self.create_user.name}")
        self.assertEqual(response.data["email"], self.create_user.email)
        self.assertEqual(response.data["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data["role"]["name"], self.create_user.role.name)

    def test_user_name_min_length(self):
        """
        Test that the name must be at least 3 characters long when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"][:2],
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0], "Name must be at least 3 characters long."
        )
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": self.create_user.name[:2],
                "email": self.create_user.email,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0], "Name must be at least 3 characters long."
        )

    def test_user_name_max_length(self):
        """
        Test that the name cannot be more than 50 characters long when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"][0] * 51,
                "email": self.new_user_data["email"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name cannot exceed 50 characters.")
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": self.create_user.name[0] * 51,
                "email": self.create_user.email,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Name cannot exceed 50 characters.")

    def test_user_email_blank(self):
        """
        Test that a user cannot be created or updated with a blank email.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": "",
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Email address is required.")
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": self.create_user.name,
                "email": "",
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Email address is required.")

    def test_user_email_required(self):
        """
        Test that the email is required when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Email address is required.")
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": self.create_user.name,
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Email address is required.")

    def test_user_email_whitespace(self):
        """
        Test that leading/trailing whitespace in the email is stripped when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": f"  {self.new_user_data["email"]}  ",
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertIn("password", response.data)
        self.assertEqual(response.data["name"], self.new_user_data["name"])
        self.assertEqual(response.data["email"], self.new_user_data["email"])
        self.assertEqual(response.data["role"]["id"], self.view_role.id)
        self.assertEqual(response.data["role"]["name"], self.view_role.name)
        created_user = User.objects.get(email=self.new_user_data["email"])
        self.assertTrue(created_user.is_manually_created)
        self.assertIsNotNone(created_user.temp_plaintext_password)
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": self.create_user.name,
                "email": f"  {self.create_user.email}  ",
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["id"], self.create_user.id)
        self.assertEqual(response.data["name"], self.create_user.name)
        self.assertEqual(response.data["email"], self.create_user.email)
        self.assertEqual(response.data["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data["role"]["name"], self.create_user.role.name)

    def test_user_email_case_insensitive(self):
        """
        Test that the email is case insensitive when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": self.new_user_data["email"].upper(),
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertIn("password", response.data)
        self.assertEqual(response.data["name"], self.new_user_data["name"])
        self.assertEqual(response.data["email"], self.new_user_data["email"])
        self.assertEqual(response.data["role"]["id"], self.view_role.id)
        self.assertEqual(response.data["role"]["name"], self.view_role.name)
        created_user = User.objects.get(email=self.new_user_data["email"])
        self.assertTrue(created_user.is_manually_created)
        self.assertIsNotNone(created_user.temp_plaintext_password)
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": self.create_user.name,
                "email": self.create_user.email.upper(),
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("id", response.data["role"])
        self.assertIn("name", response.data["role"])
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["id"], self.create_user.id)
        self.assertEqual(response.data["name"], self.create_user.name)
        self.assertEqual(response.data["email"], self.create_user.email)
        self.assertEqual(response.data["role"]["id"], self.create_user.role.id)
        self.assertEqual(response.data["role"]["name"], self.create_user.role.name)

    def test_user_email_invalid_format(self):
        """
        Test that the email follows a valid email format when creating or updating a user.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.users_url,
            {
                "name": self.new_user_data["name"],
                "email": self.new_user_data["email"].replace(".com", ""),
                "role_id": self.view_role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Enter a valid email address.")
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.user_url(self.create_user.id),
            {
                "name": self.create_user.name,
                "email": self.create_user.email.replace(".com", ""),
                "role_id": self.create_user.role.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "Enter a valid email address.")

    def test_delete_user_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to deleting users.
        """
        response = self.client.delete(self.user_url(self.view_user.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_self(self):
        """
        Test that authenticated users who do not have delete_user permission can delete their own account.
        """
        new_user = User.objects.create_user(
            name=self.new_user_data["name"],
            email=self.new_user_data["email"],
            password=self.new_user_data["password"],
            role=self.view_role,
        )
        self.authenticate(
            email=self.new_user_data["email"],
            password=self.new_user_data["password"],
        )
        response = self.client.delete(self.user_url(new_user.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_user_no_permission(self):
        """
        Test that authenticated users who do not have delete_user permission cannot delete a user.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.delete(self.user_url(self.create_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to delete this user.",
        )

    def test_delete_superuser(self):
        """
        Test that authenticated users who have delete_user permission cannot delete a superuser.
        """
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
        )
        response = self.client.delete(self.user_url(self.admin_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot delete a superuser.",
        )

    def test_delete_user(self):
        """
        Test that authenticated users with delete_user permission can delete a user.
        """
        new_user = User.objects.create_user(
            name=self.new_user_data["name"],
            email=self.new_user_data["email"],
            password=self.new_user_data["password"],
            role=self.view_role,
        )
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
        )
        response = self.client.delete(self.user_url(new_user.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_not_found(self):
        """
        Test that authenticated users who have delete_user permission deleting a non-existent user get an appropriate error response.
        """
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
        )
        response = self.client.delete(self.user_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "User not found.")
