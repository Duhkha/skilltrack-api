import io
import csv
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from permissions.models import PermissionGroup, Permission
from users.models import User, Role


class UserBulkIngestTests(APITestCase):
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
        self.ingest_role = Role.objects.create(name="updater")

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
        self.ingest_role.permissions.set(
            [
                self.create_role_permission,
                self.update_role_permission,
                self.create_user_permission,
                self.update_user_permission,
            ]
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
        self.ingest_user_data = {
            "name": "Ingester",
            "email": "ingester@example.com",
            "password": "Ingester123!",
        }
        self.bulk_user_data_1 = {
            "name": "Bulk User 1",
            "email": "bulkuser1@example.com",
            "password": "BulkUser123!",
        }
        self.bulk_user_data_2 = {
            "name": "Bulk User 2",
            "email": "bulkuser2@example.com",
            "password": "BulkUser123!",
        }
        self.bulk_user_data_3 = {
            "name": "Bulk User 3",
            "email": "bulkuser3@example.com",
            "password": "BulkUser123!",
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
        self.ingest_user = User.objects.create_user(
            name=self.ingest_user_data["name"],
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
            role=self.ingest_role,
        )

        self.sign_in_url = reverse("sign-in")
        self.bulk_ingest_url = reverse("bulk-ingest-ingest-csv")

    def _create_csv_file(self, rows):
        """
        Helper method to create a CSV file for testing purposes.
        """
        fieldnames = ["name", "email", "role"]

        csv_file = io.StringIO()

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

        csv_file.seek(0)

        return SimpleUploadedFile(
            "test.csv", csv_file.getvalue().encode(), content_type="text/csv"
        )

    def authenticate(self, email, password):
        response = self.client.post(
            self.sign_in_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_bulk_ingest_access_denied_without_auth(self):
        """
        Test that unauthenticated users are denied access to bulk ingest.
        """
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": self.bulk_user_data_2["name"],
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )

        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bulk_ingest_no_permission(self):
        """
        Test that authenticated users who do not have create_user and update_user permission cannot perform bulk ingest.
        """
        self.authenticate(
            email=self.view_user_data["email"], password=self.view_user_data["password"]
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": self.bulk_user_data_2["name"],
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to bulk ingest users.",
        )

    def test_bulk_ingest_missing_file(self):
        """
        Test that authenticated users get an appropriate error response when no file is uploaded.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        response = self.client.post(self.bulk_ingest_url, {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "CSV file is required.")

    def test_bulk_ingest_invalid_utf8_file(self):
        """
        Test that authenticated users get an appropriate error response when uploaded file is not properly UTF-8 encoded.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        invalid_content = (
            "name,email,role\nBulk Usér 1,bulkuser1@example.com,viewer".encode(
                "latin-1"
            )
        )
        file = SimpleUploadedFile(
            "invalid.csv", invalid_content, content_type="text/csv"
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Uploaded file is not a valid UTF-8 encoded text file.",
        )

    def test_bulk_ingest_invalid_csv_format(self):
        """
        Test that authenticated users get an appropriate error response when the uploaded file is not a valid CSV format.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        invalid_csv_data = (
            "This is not even close to CSV structure.\nJust some random text!"
        )
        file = SimpleUploadedFile(
            "not_a_csv.csv", invalid_csv_data.encode("utf-8"), content_type="text/csv"
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "Uploaded file does not appear to be a valid CSV."
        )

    def test_bulk_ingest_csv_missing_required_columns(self):
        """
        Test that authenticated users get an appropriate error response when the uploaded file is a CSV missing one or more required columns.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        csv_missing_columns = "name,email\nBulk User 1,bulkuser1@example.com"
        file = SimpleUploadedFile(
            "missing_columns.csv",
            csv_missing_columns.encode("utf-8"),
            content_type="text/csv",
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "CSV must include these columns: name, email, role.",
        )

    def test_bulk_ingest_create(self):
        """
        Test that authenticated users who have create_user and update_user permission can successfully bulk create users.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": self.bulk_user_data_2["name"],
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 2)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 0)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 0)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 2)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertIn("id", response.data["users"]["created"][0])
        self.assertIn("name", response.data["users"]["created"][0])
        self.assertIn("email", response.data["users"]["created"][0])
        self.assertIn("role", response.data["users"]["created"][0])
        self.assertIn("id", response.data["users"]["created"][0]["role"])
        self.assertIn("name", response.data["users"]["created"][0]["role"])
        self.assertEqual(
            response.data["users"]["created"][0]["name"], self.bulk_user_data_1["name"]
        )
        self.assertEqual(
            response.data["users"]["created"][1]["name"], self.bulk_user_data_2["name"]
        )
        self.assertEqual(
            response.data["users"]["created"][0]["email"],
            self.bulk_user_data_1["email"],
        )
        self.assertEqual(
            response.data["users"]["created"][1]["email"],
            self.bulk_user_data_2["email"],
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["created"][1]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["name"], self.view_role.name
        )
        self.assertEqual(
            response.data["users"]["created"][1]["role"]["name"], self.view_role.name
        )
        self.assertIn("password", response.data["users"]["created"][0])
        self.assertIn("password", response.data["users"]["created"][1])
        created_bulk_user_1 = User.objects.get(email=self.bulk_user_data_1["email"])
        created_bulk_user_2 = User.objects.get(email=self.bulk_user_data_2["email"])
        self.assertTrue(created_bulk_user_1.is_manually_created)
        self.assertTrue(created_bulk_user_2.is_manually_created)
        self.assertIsNotNone(created_bulk_user_1.temp_plaintext_password)
        self.assertIsNotNone(created_bulk_user_2.temp_plaintext_password)

    def test_bulk_ingest_update(self):
        """
        Test that authenticated users who have create_user and update_user permission can successfully bulk update users.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_1["name"],
            email=self.bulk_user_data_1["email"],
            password=self.bulk_user_data_1["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": f"Updated {self.bulk_user_data_1['name']}",
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": f"Updated {self.bulk_user_data_2['name']}",
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 2)
        self.assertEqual(response.data["summary"]["validation_errors"], 0)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 0)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 2)
        self.assertIn("id", response.data["users"]["updated"][0])
        self.assertIn("name", response.data["users"]["updated"][0])
        self.assertIn("email", response.data["users"]["updated"][0])
        self.assertIn("role", response.data["users"]["updated"][0])
        self.assertIn("id", response.data["users"]["updated"][0]["role"])
        self.assertIn("name", response.data["users"]["updated"][0]["role"])
        self.assertEqual(
            response.data["users"]["updated"][0]["name"],
            f"Updated {self.bulk_user_data_1['name']}",
        )
        self.assertEqual(
            response.data["users"]["updated"][1]["name"],
            f"Updated {self.bulk_user_data_2['name']}",
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["email"],
            self.bulk_user_data_1["email"],
        )
        self.assertEqual(
            response.data["users"]["updated"][1]["email"],
            self.bulk_user_data_2["email"],
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["updated"][1]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["role"]["name"], self.view_role.name
        )
        self.assertEqual(
            response.data["users"]["updated"][1]["role"]["name"], self.view_role.name
        )
        self.assertNotIn("password", response.data["users"]["updated"][0])
        self.assertNotIn("password", response.data["users"]["updated"][1])

    def test_bulk_ingest_invalid_role(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error when the uploaded file contains an invalid role.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"],
                    "role": "nonexistent_role",
                },
                {
                    "name": f"Updated {self.bulk_user_data_2['name']}",
                    "email": self.bulk_user_data_2["email"],
                    "role": "nonexistent_role",
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 2)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 2)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertEqual(response.data["summary"]["errors"][1]["row"], 2)
        self.assertIn("role", response.data["summary"]["errors"][0]["errors"])
        self.assertIn("role", response.data["summary"]["errors"][1]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["role"][0],
            "Role nonexistent_role not found.",
        )
        self.assertEqual(
            response.data["summary"]["errors"][1]["errors"]["role"][0],
            "Role nonexistent_role not found.",
        )

    def test_bulk_ingest_superuser_role(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the assigned role is a superuser role.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"],
                    "role": self.admin_role.name,
                },
                {
                    "name": self.bulk_user_data_2["name"],
                    "email": self.bulk_user_data_2["email"],
                    "role": self.admin_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 2)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 2)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertEqual(response.data["summary"]["errors"][1]["row"], 2)
        self.assertIn("role", response.data["summary"]["errors"][0]["errors"])
        self.assertIn("role", response.data["summary"]["errors"][1]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["role"][0],
            "Role admin is a superuser role.",
        )
        self.assertEqual(
            response.data["summary"]["errors"][1]["errors"]["role"][0],
            "Role admin is a superuser role.",
        )

    def test_bulk_ingest_partial_success(self):
        """
        Test that authenticated users who have create_user and update_user permission receive a partial success response when some records are valid and others are not.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": f"Updated {self.bulk_user_data_2['name']}",
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": f"Invalid {self.bulk_user_data_3['name']}",
                    "email": self.bulk_user_data_3["email"],
                    "role": self.admin_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 3)
        self.assertEqual(response.data["summary"]["created"], 1)
        self.assertEqual(response.data["summary"]["updated"], 1)
        self.assertEqual(response.data["summary"]["validation_errors"], 1)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 1)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 1)
        self.assertEqual(len(response.data["users"]["updated"]), 1)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 3)
        self.assertIn("role", response.data["summary"]["errors"][0]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["role"][0],
            "Role admin is a superuser role.",
        )
        self.assertIn("id", response.data["users"]["created"][0])
        self.assertIn("id", response.data["users"]["updated"][0])
        self.assertIn("name", response.data["users"]["created"][0])
        self.assertIn("name", response.data["users"]["updated"][0])
        self.assertIn("email", response.data["users"]["created"][0])
        self.assertIn("email", response.data["users"]["updated"][0])
        self.assertIn("role", response.data["users"]["created"][0])
        self.assertIn("role", response.data["users"]["updated"][0])
        self.assertIn("id", response.data["users"]["created"][0]["role"])
        self.assertIn("id", response.data["users"]["updated"][0]["role"])
        self.assertIn("name", response.data["users"]["created"][0]["role"])
        self.assertIn("name", response.data["users"]["updated"][0]["role"])
        self.assertEqual(
            response.data["users"]["created"][0]["name"], self.bulk_user_data_1["name"]
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["name"],
            f"Updated {self.bulk_user_data_2['name']}",
        )
        self.assertEqual(
            response.data["users"]["created"][0]["email"],
            self.bulk_user_data_1["email"],
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["email"],
            self.bulk_user_data_2["email"],
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["name"], self.view_role.name
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["role"]["name"], self.view_role.name
        )
        self.assertIn("password", response.data["users"]["created"][0])
        self.assertNotIn("password", response.data["users"]["updated"][0])
        created_bulk_user_1 = User.objects.get(email=self.bulk_user_data_1["email"])
        self.assertTrue(created_bulk_user_1.is_manually_created)
        self.assertIsNotNone(created_bulk_user_1.temp_plaintext_password)

    def test_bulk_ingest_name_blank(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the name field is blank.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": "",
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": "",
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 2)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 2)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertEqual(response.data["summary"]["errors"][1]["row"], 2)
        self.assertIn("name", response.data["summary"]["errors"][0]["errors"])
        self.assertIn("name", response.data["summary"]["errors"][1]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["name"][0],
            "Name is required.",
        )
        self.assertEqual(
            response.data["summary"]["errors"][1]["errors"]["name"][0],
            "Name is required.",
        )

    def test_bulk_ingest_name_required(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the name field is required.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 2)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 2)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertEqual(response.data["summary"]["errors"][1]["row"], 2)
        self.assertIn("name", response.data["summary"]["errors"][0]["errors"])
        self.assertIn("name", response.data["summary"]["errors"][1]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["name"][0],
            "Name is required.",
        )
        self.assertEqual(
            response.data["summary"]["errors"][1]["errors"]["name"][0],
            "Name is required.",
        )

    def test_bulk_ingest_name_whitespace(self):
        """
        Test that authenticated users who have create_user and update_user permission can successfully bulk create users where leading/trailing whitespace in the name is stripped.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": f"      {self.bulk_user_data_1["name"]}  ",
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": f"     Updated {self.bulk_user_data_2["name"]}   ",
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 1)
        self.assertEqual(response.data["summary"]["updated"], 1)
        self.assertEqual(response.data["summary"]["validation_errors"], 0)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 0)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 1)
        self.assertEqual(len(response.data["users"]["updated"]), 1)
        self.assertIn("id", response.data["users"]["created"][0])
        self.assertIn("id", response.data["users"]["updated"][0])
        self.assertIn("name", response.data["users"]["created"][0])
        self.assertIn("name", response.data["users"]["updated"][0])
        self.assertIn("email", response.data["users"]["created"][0])
        self.assertIn("email", response.data["users"]["updated"][0])
        self.assertIn("role", response.data["users"]["created"][0])
        self.assertIn("role", response.data["users"]["updated"][0])
        self.assertIn("id", response.data["users"]["created"][0]["role"])
        self.assertIn("id", response.data["users"]["updated"][0]["role"])
        self.assertIn("name", response.data["users"]["created"][0]["role"])
        self.assertIn("name", response.data["users"]["updated"][0]["role"])
        self.assertEqual(
            response.data["users"]["created"][0]["name"], self.bulk_user_data_1["name"]
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["name"],
            f"Updated {self.bulk_user_data_2['name']}",
        )
        self.assertEqual(
            response.data["users"]["created"][0]["email"],
            self.bulk_user_data_1["email"],
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["email"],
            self.bulk_user_data_2["email"],
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["name"], self.view_role.name
        )
        self.assertEqual(
            response.data["users"]["updated"][0]["role"]["name"], self.view_role.name
        )
        self.assertIn("password", response.data["users"]["created"][0])
        self.assertNotIn("password", response.data["users"]["updated"][0])
        created_bulk_user_1 = User.objects.get(email=self.bulk_user_data_1["email"])
        self.assertTrue(created_bulk_user_1.is_manually_created)
        self.assertIsNotNone(created_bulk_user_1.temp_plaintext_password)

    def test_bulk_ingest_name_min_length(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the name field is short.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"][:2],
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": self.bulk_user_data_2["name"][:2],
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 2)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 2)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertEqual(response.data["summary"]["errors"][1]["row"], 2)
        self.assertIn("name", response.data["summary"]["errors"][0]["errors"])
        self.assertIn("name", response.data["summary"]["errors"][1]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["name"][0],
            "Name must be at least 3 characters long.",
        )
        self.assertEqual(
            response.data["summary"]["errors"][1]["errors"]["name"][0],
            "Name must be at least 3 characters long.",
        )

    def test_bulk_ingest_name_max_length(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the name field is too long.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        User.objects.create_user(
            name=self.bulk_user_data_2["name"],
            email=self.bulk_user_data_2["email"],
            password=self.bulk_user_data_2["password"],
            role=self.view_role,
            is_manually_created=True,
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"][0] * 51,
                    "email": self.bulk_user_data_1["email"],
                    "role": self.view_role.name,
                },
                {
                    "name": self.bulk_user_data_2["name"][0] * 51,
                    "email": self.bulk_user_data_2["email"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 2)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 2)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 2)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertEqual(response.data["summary"]["errors"][1]["row"], 2)
        self.assertIn("name", response.data["summary"]["errors"][0]["errors"])
        self.assertIn("name", response.data["summary"]["errors"][1]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["name"][0],
            "Name cannot exceed 50 characters.",
        )
        self.assertEqual(
            response.data["summary"]["errors"][1]["errors"]["name"][0],
            "Name cannot exceed 50 characters.",
        )

    def test_bulk_ingest_email_blank(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the email field is blank.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": "",
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 1)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 1)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 1)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertIn("email", response.data["summary"]["errors"][0]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["email"][0],
            "Email address is required.",
        )

    def test_bulk_ingest_email_required(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the email field is required.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 1)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 1)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 1)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertIn("email", response.data["summary"]["errors"][0]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["email"][0],
            "Email address is required.",
        )

    def test_bulk_ingest_email_whitespace(self):
        """
        Test that authenticated users who have create_user and update_user permission can successfully bulk create users where leading/trailing whitespace in the email is stripped.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": f"       {self.bulk_user_data_1["email"]}      ",
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 1)
        self.assertEqual(response.data["summary"]["created"], 1)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 0)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 0)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 1)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertIn("id", response.data["users"]["created"][0])
        self.assertIn("name", response.data["users"]["created"][0])
        self.assertIn("email", response.data["users"]["created"][0])
        self.assertIn("role", response.data["users"]["created"][0])
        self.assertIn("id", response.data["users"]["created"][0]["role"])
        self.assertIn("name", response.data["users"]["created"][0]["role"])
        self.assertEqual(
            response.data["users"]["created"][0]["name"], self.bulk_user_data_1["name"]
        )
        self.assertEqual(
            response.data["users"]["created"][0]["email"],
            self.bulk_user_data_1["email"],
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["name"], self.view_role.name
        )
        self.assertIn("password", response.data["users"]["created"][0])
        created_bulk_user_1 = User.objects.get(email=self.bulk_user_data_1["email"])
        self.assertTrue(created_bulk_user_1.is_manually_created)
        self.assertIsNotNone(created_bulk_user_1.temp_plaintext_password)

    def test_bulk_ingest_email_case_insensitive(self):
        """
        Test that authenticated users who have create_user and update_user permission can successfully bulk create users where email is case insensitive.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"].upper(),
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 1)
        self.assertEqual(response.data["summary"]["created"], 1)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 0)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 0)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 1)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertIn("id", response.data["users"]["created"][0])
        self.assertIn("name", response.data["users"]["created"][0])
        self.assertIn("email", response.data["users"]["created"][0])
        self.assertIn("role", response.data["users"]["created"][0])
        self.assertIn("id", response.data["users"]["created"][0]["role"])
        self.assertIn("name", response.data["users"]["created"][0]["role"])
        self.assertEqual(
            response.data["users"]["created"][0]["name"], self.bulk_user_data_1["name"]
        )
        self.assertEqual(
            response.data["users"]["created"][0]["email"],
            self.bulk_user_data_1["email"],
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["id"], self.view_role.id
        )
        self.assertEqual(
            response.data["users"]["created"][0]["role"]["name"], self.view_role.name
        )
        self.assertIn("password", response.data["users"]["created"][0])
        created_bulk_user_1 = User.objects.get(email=self.bulk_user_data_1["email"])
        self.assertTrue(created_bulk_user_1.is_manually_created)
        self.assertIsNotNone(created_bulk_user_1.temp_plaintext_password)

    def test_bulk_ingest_email_invalid_format(self):
        """
        Test that authenticated users who have create_user and update_user permission get an appropriate error response when the email field has invalid format.
        """
        self.authenticate(
            email=self.ingest_user_data["email"],
            password=self.ingest_user_data["password"],
        )
        file = self._create_csv_file(
            [
                {
                    "name": self.bulk_user_data_1["name"],
                    "email": self.bulk_user_data_1["email"].replace(".com", ""),
                    "role": self.view_role.name,
                },
            ]
        )
        response = self.client.post(
            self.bulk_ingest_url, {"file": file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["total_rows"], 1)
        self.assertEqual(response.data["summary"]["created"], 0)
        self.assertEqual(response.data["summary"]["updated"], 0)
        self.assertEqual(response.data["summary"]["validation_errors"], 1)
        self.assertEqual(response.data["summary"]["db_errors"], 0)
        self.assertEqual(len(response.data["summary"]["errors"]), 1)
        self.assertIn("users", response.data)
        self.assertIn("created", response.data["users"])
        self.assertIn("updated", response.data["users"])
        self.assertEqual(len(response.data["users"]["created"]), 0)
        self.assertEqual(len(response.data["users"]["updated"]), 0)
        self.assertEqual(response.data["summary"]["errors"][0]["row"], 1)
        self.assertIn("email", response.data["summary"]["errors"][0]["errors"])
        self.assertEqual(
            response.data["summary"]["errors"][0]["errors"]["email"][0],
            "Enter a valid email address.",
        )
