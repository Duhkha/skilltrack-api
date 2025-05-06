from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from permissions.models import Permission, PermissionGroup
from roles.models import Role
from users.models import User


class RoleTests(APITestCase):
    def setUp(self):
        self.roles_permission_group = PermissionGroup.objects.create(
            name="roles", description="Permissions related to role management."
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
            ]
        )
        self.view_role.permissions.set([self.view_role_permission])
        self.create_role.permissions.set([self.create_role_permission])
        self.update_role.permissions.set([self.update_role_permission])
        self.delete_role.permissions.set([self.delete_role_permission])

        self.new_role_data = {
            "name": "new_role",
        }
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
        self.no_role_user_data = {
            "name": "No Role",
            "email": "norole@example.com",
            "password": "NoRole123!",
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
        self.no_role_user = User.objects.create_user(
            name=self.no_role_user_data["name"],
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )

        self.sign_in_url = reverse("sign-in")
        self.roles_url = reverse("roles-list")
        self.role_url = lambda group_id: reverse("roles-detail", args=[group_id])

    def authenticate(self, email, password):
        response = self.client.post(
            self.sign_in_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return response

    def test_roles_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to roles.
        """
        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_roles_no_permission(self):
        """
        Test that authenticated users who do not have view_role permission but are assigned a role cannot get all roles, except themselves.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertEqual(response.data[0]["name"], self.create_role.name)
        self.assertIn("users", response.data[0])
        self.assertIn("groupedPermissions", response.data[0])

    def test_roles_superuser(self):
        """
        Test that authenticated users who are superusers can get all roles.
        """
        self.authenticate(
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
        )
        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertEqual(response.data[0]["name"], self.admin_role.name)
        self.assertIn("users", response.data[0])
        self.assertIn("groupedPermissions", response.data[0])

    def test_roles_non_superuser_has_permission(self):
        """
        Test that authenticated users who are not superusers and who have view_role permission can get all roles, except superuser roles.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertEqual(response.data[0]["name"], self.view_role.name)
        self.assertIn("users", response.data[0])
        self.assertIn("groupedPermissions", response.data[0])
        for role in response.data:
            self.assertNotEqual(role["name"], self.admin_role.name)

    def test_roles_superuser_search_by_role_name(self):
        """
        Test that authenticated users who are superusers can search roles by role name.
        """
        self.authenticate(
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
        )
        response = self.client.get(self.roles_url, {"search": self.admin_role.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("id", response.data[0])
        self.assertIn("name", response.data[0])
        self.assertEqual(response.data[0]["name"], self.admin_role.name)
        self.assertIn("users", response.data[0])
        self.assertIn("groupedPermissions", response.data[0])
        response = self.client.get(self.roles_url, {"search": "ter"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_roles_non_superuser_has_permission_search_by_role_name(self):
        """
        Test that authenticated users who are not superusers and who have view_role permission can search roles by role name, except superuser roles.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.roles_url, {"search": self.admin_role.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        response = self.client.get(self.roles_url, {"search": "ter"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_role_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to a role.
        """
        response = self.client.get(self.role_url(self.view_role.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_no_permission(self):
        """
        Test that authenticated users who do not have view_role permission cannot get any role, except their own.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.get(self.role_url(self.view_role.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to view this role.",
        )
        response = self.client.get(self.role_url(self.create_role.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.create_role.name)
        self.assertIn("users", response.data)
        self.assertIn("groupedPermissions", response.data)

    def test_role_superuser(self):
        """
        Test that authenticated users who are superusers can get any role.
        """
        self.authenticate(
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
        )
        response = self.client.get(self.role_url(self.view_role.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.view_role.name)
        self.assertIn("users", response.data)
        self.assertIn("groupedPermissions", response.data)

    def test_role_user_no_role(self):
        """
        Test that authenticated users who do not have an assigned role get an appropriate error response.
        """
        self.authenticate(
            email=self.no_role_user_data["email"],
            password=self.no_role_user_data["password"],
        )
        response = self.client.get(self.role_url(self.view_role.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "User has no assigned role.",
        )

    def test_role_non_superuser_has_permission(self):
        """
        Test that authenticated users who are not superusers and who have view_role permission can get any role, except superuser roles.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.get(self.role_url(self.view_role.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.view_role.name)
        self.assertIn("users", response.data)
        self.assertIn("groupedPermissions", response.data)
        response = self.client.get(self.role_url(self.admin_role.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_not_found(self):
        """
        Test that authenticated users who have view_role permission retrieving a non-existent role get an appropriate error response.
        """
        self.authenticate(
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
        )
        response = self.client.get(self.role_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_role_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to creating a role.
        """
        response = self.client.post(
            self.roles_url,
            {"name": self.new_role_data["name"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_role_no_permission(self):
        """
        Test that authenticated users who do not have create_role permission cannot create a role.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {"name": self.new_role_data["name"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to create a role.",
        )

    def test_create_role_has_permission_self_assignment(self):
        """
        Test that authenticated users who have create_role permission cannot assign a role to themselves.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {
                "name": self.new_role_data["name"],
                "permission_ids": [],
                "user_ids": [self.create_user.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot assign roles to yourself.",
        )

    def test_create_role_has_permission_superuser_assignment(self):
        """
        Test that authenticated users who have create_role permission cannot assign a role to superusers.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {
                "name": self.new_role_data["name"],
                "permission_ids": [],
                "user_ids": [self.admin_user.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot assign roles to superusers.",
        )

    def test_create_role_exists(self):
        """
        Test that authenticated users who have create_role permission cannot create a role with the same name as an existing role.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {
                "name": self.view_role.name,
                "permission_ids": [],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0],
            "Role with this name already exists.",
        )

    def test_create_role_with_all_permissions_exists(self):
        """
        Test that authenticated users who have create_role permission cannot create a role with all permissions assigned since it already exists.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {
                "name": self.new_role_data["name"],
                "permission_ids": [
                    self.view_role_permission.id,
                    self.create_role_permission.id,
                    self.update_role_permission.id,
                    self.delete_role_permission.id,
                ],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "A role with all permissions already exists.",
        )

    def test_create_role_permission_ids_not_found(self):
        """
        Test that authenticated users who have create_role permission cannot create a role with non-existent permissions.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {
                "name": self.new_role_data["name"],
                "permission_ids": [99999],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["permission_ids"][0],
            "One or more of the provided permissions could not be found.",
        )

    def test_create_role_user_ids_not_found(self):
        """
        Test that authenticated users who have create_role permission cannot create a role with non-existent users.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {
                "name": self.new_role_data["name"],
                "permission_ids": [],
                "user_ids": [99999],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["user_ids"][0],
            "One or more of the provided users could not be found.",
        )

    def test_create_role(self):
        """
        Test that authenticated users who have create_role permission can create a role.
        """
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
        )
        response = self.client.post(
            self.roles_url,
            {
                "name": self.new_role_data["name"],
                "permission_ids": [],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.new_role_data["name"])
        self.assertIn("users", response.data)
        self.assertIn("groupedPermissions", response.data)

    def test_update_role_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to updating a role.
        """
        response = self.client.put(
            self.role_url(self.view_role.id),
            {"name": f"updated_{self.view_role.name}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_role_no_permission(self):
        """
        Test that authenticated users who do not have update_role permission cannot update a role.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.create_role.id),
            {"name": f"updated_{self.create_role.name}"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to update this role.",
        )

    def test_update_role_has_permission_own_role(self):
        """
        Test that authenticated users who have update_role permission cannot update their own role.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.update_role.id),
            {
                "name": f"updated_{self.update_role.name}",
                "permission_ids": [],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot update your own role.",
        )

    def test_update_role_has_permission_superuser_role(self):
        """
        Test that authenticated users who have update_role permission cannot update a role that has superusers in it.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.admin_role.id),
            {
                "name": f"updated_{self.admin_role.name}",
                "permission_ids": [],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot update a superuser role.",
        )

    def test_update_role_has_permission_self_assignment(self):
        """
        Test that authenticated users who have update_role permission cannot assign a role to themselves.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.view_role.id),
            {
                "name": f"updated_{self.view_role.name}",
                "permission_ids": [],
                "user_ids": [self.update_user.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot assign roles to yourself.",
        )

    def test_update_role_has_permission_superuser_assignment(self):
        """
        Test that authenticated users who have update_role permission cannot assign a role to superusers.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.view_role.id),
            {
                "name": f"updated_{self.view_role.name}",
                "permission_ids": [],
                "user_ids": [self.admin_user.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot assign roles to superusers.",
        )

    def test_update_role_exists(self):
        """
        Test that authenticated users who have update_role permission cannot update a role with the same name as an existing role.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.create_role.id),
            {
                "name": self.view_role.name,
                "permission_ids": [],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0],
            "Role with this name already exists.",
        )

    def test_update_role_with_all_permissions_exists(self):
        """
        Test that authenticated users who have update_role permission cannot update a role with all permissions assigned since it already exists.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.view_role.id),
            {
                "name": f"updated_{self.view_role.name}",
                "permission_ids": [
                    self.view_role_permission.id,
                    self.create_role_permission.id,
                    self.update_role_permission.id,
                    self.delete_role_permission.id,
                ],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "A role with all permissions already exists.",
        )

    def test_update_role_permission_ids_not_found(self):
        """
        Test that authenticated users who have update_role permission cannot update a role with non-existent permissions.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.view_role.id),
            {
                "name": f"updated_{self.view_role.name}",
                "permission_ids": [99999],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["permission_ids"][0],
            "One or more of the provided permissions could not be found.",
        )

    def test_update_role_user_ids_not_found(self):
        """
        Test that authenticated users who have update_role permission cannot update a role with non-existent users.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.view_role.id),
            {
                "name": f"updated_{self.view_role.name}",
                "permission_ids": [],
                "user_ids": [99999],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["user_ids"][0],
            "One or more of the provided users could not be found.",
        )

    def test_update_role(self):
        """
        Test that authenticated users who have update_role permission can update a role.
        """
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
        )
        response = self.client.put(
            self.role_url(self.view_role.id),
            {
                "name": f"updated_{self.view_role.name}",
                "permission_ids": [self.view_role_permission.id],
                "user_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], f"updated_{self.view_role.name}")
        self.assertIn("users", response.data)
        self.assertIn("groupedPermissions", response.data)

    def test_delete_role_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to deleting a role.
        """
        response = self.client.delete(self.role_url(self.view_role.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_role_no_permission(self):
        """
        Test that authenticated users who do not have delete_role permission cannot delete a role.
        """
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
        )
        response = self.client.delete(self.role_url(self.create_role.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to delete this role.",
        )

    def test_delete_role_has_permission_own_role(self):
        """
        Test that authenticated users who have delete_role permission cannot delete their own role.
        """
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
        )
        response = self.client.delete(self.role_url(self.delete_role.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot delete your own role.",
        )

    def test_delete_role_has_permission_superuser_role(self):
        """
        Test that authenticated users who have delete_role permission cannot delete a superuser role.
        """
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
        )
        response = self.client.delete(self.role_url(self.admin_role.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You cannot delete a superuser role.",
        )

    def test_delete_role_not_found(self):
        """
        Test that authenticated users who have delete_role permission cannot delete a non-existent role.
        """
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
        )
        response = self.client.delete(self.role_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_role(self):
        """
        Test that authenticated users who have delete_role permission can delete a role.
        """
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
        )
        response = self.client.delete(self.role_url(self.view_role.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
