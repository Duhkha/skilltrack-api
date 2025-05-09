from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from skills.models import Level, Skill
from users.models import User
from permissions.models import Permission, PermissionGroup
from roles.models import Role
from .serializers import LevelSerializer


class LevelTests(APITestCase):
    def setUp(self):
        # Create permission groups
        self.levels_permission_group = PermissionGroup.objects.create(
            name="levels", description="Permissions related to level management."
        )

        # Create level permissions
        self.view_level_permission = Permission.objects.create(
            name="view_level",
            description="Permission to view levels.",
            group=self.levels_permission_group,
        )
        self.create_level_permission = Permission.objects.create(
            name="create_level",
            description="Permission to create a new level.",
            group=self.levels_permission_group,
        )
        self.update_level_permission = Permission.objects.create(
            name="update_level",
            description="Permission to update an existing level.",
            group=self.levels_permission_group,
        )
        self.delete_level_permission = Permission.objects.create(
            name="delete_level",
            description="Permission to delete a level.",
            group=self.levels_permission_group,
        )
        
        # Create roles with different permissions
        self.admin_role = Role.objects.create(name="admin")
        self.view_role = Role.objects.create(name="viewer")
        self.create_role = Role.objects.create(name="creator")
        self.update_role = Role.objects.create(name="updater")
        self.delete_role = Role.objects.create(name="deleter")
        
        # Assign permissions to roles
        self.admin_role.permissions.set([
            self.view_level_permission,
            self.create_level_permission,
            self.update_level_permission,
            self.delete_level_permission
        ])
        self.view_role.permissions.set([self.view_level_permission])
        self.create_role.permissions.set([self.create_level_permission])
        self.update_role.permissions.set([self.update_level_permission])
        self.delete_role.permissions.set([self.delete_level_permission])
        
        # Create test users with different roles
        self.admin_user_data = {
            "name": "Admin User",
            "email": "admin@example.com",
            "password": "Admin123!"
        }
        self.view_user_data = {
            "name": "Viewer User",
            "email": "viewer@example.com",
            "password": "Viewer123!"
        }
        self.create_user_data = {
            "name": "Creator User",
            "email": "creator@example.com",
            "password": "Creator123!"
        }
        self.update_user_data = {
            "name": "Updater User",
            "email": "updater@example.com",
            "password": "Updater123!"
        }
        self.delete_user_data = {
            "name": "Deleter User",
            "email": "deleter@example.com",
            "password": "Deleter123!"
        }
        self.regular_user_data = {
            "name": "Regular User",
            "email": "regular@example.com",
            "password": "Regular123!"
        }
        
        self.admin_user = User.objects.create_superuser(
            name=self.admin_user_data["name"],
            email=self.admin_user_data["email"],
            password=self.admin_user_data["password"],
            role=self.admin_role
        )
        self.view_user = User.objects.create_user(
            name=self.view_user_data["name"],
            email=self.view_user_data["email"],
            password=self.view_user_data["password"],
            role=self.view_role
        )
        self.create_user = User.objects.create_user(
            name=self.create_user_data["name"],
            email=self.create_user_data["email"],
            password=self.create_user_data["password"],
            role=self.create_role
        )
        self.update_user = User.objects.create_user(
            name=self.update_user_data["name"],
            email=self.update_user_data["email"],
            password=self.update_user_data["password"],
            role=self.update_role
        )
        self.delete_user = User.objects.create_user(
            name=self.delete_user_data["name"],
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"],
            role=self.delete_role
        )
        self.regular_user = User.objects.create_user(
            name=self.regular_user_data["name"],
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"],
        )
        
        # Create test skills
        self.python_skill = Skill.objects.create(
            name="Python",
            description="Programming language"
        )
        self.javascript_skill = Skill.objects.create(
            name="JavaScript",
            description="Web programming language"
        )
        
        # Create test levels
        self.beginner_level_data = {
            "skill_id": self.python_skill.id,
            "name": "Beginner",
            "order": 1,
            "description": "Basic Python knowledge"
        }
        self.intermediate_level_data = {
            "skill_id": self.python_skill.id,
            "name": "Intermediate",
            "order": 2,
            "description": "Intermediate Python knowledge"
        }
        self.new_level_data = {
            "skill_id": self.javascript_skill.id,
            "name": "Beginner",
            "order": 1,
            "description": "Basic JavaScript knowledge"
        }
        
        self.beginner_level = Level.objects.create(
            skill=self.python_skill,
            name=self.beginner_level_data["name"],
            order=self.beginner_level_data["order"],
            description=self.beginner_level_data["description"]
        )
        
        self.intermediate_level = Level.objects.create(
            skill=self.python_skill,
            name=self.intermediate_level_data["name"],
            order=self.intermediate_level_data["order"],
            description=self.intermediate_level_data["description"]
        )
        
        # Define URLs
        self.sign_in_url = reverse("sign-in")
        self.levels_url = reverse("level-list")
        self.level_url = lambda level_id: reverse("level-detail", args=[level_id])

    def authenticate(self, email, password):
        """Helper method to authenticate users"""
        response = self.client.post(
            self.sign_in_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    # AUTHENTICATION TESTS
    def test_levels_access_denied_without_auth(self):
        """Test that unauthenticated users are denied access to levels."""
        response = self.client.get(self.levels_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_levels_no_permission(self):
        """Test that authenticated users without view_level permission cannot get levels."""
        self.authenticate(
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"]
        )
        response = self.client.get(self.levels_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to view levels."
        )

    # LEVEL LISTING AND FILTERING TESTS
    def test_levels_with_permission(self):
        """Test that users with view_level permission can get all levels."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.levels_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two levels in the setup
        
        # Verify response structure
        level = response.data[0]
        self.assertIn("id", level)
        self.assertIn("skill_id", level)
        self.assertIn("name", level)
        self.assertIn("order", level)
        self.assertIn("description", level)
        self.assertIn("created_at", level)
        self.assertIn("updated_at", level)

    def test_levels_search_by_name(self):
        """Test searching levels by name."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(f"{self.levels_url}?search=beginner")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Beginner")

    def test_levels_search_by_description(self):
        """Test searching levels by description."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(f"{self.levels_url}?search=intermediate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Intermediate")

    def test_levels_ordering(self):
        """Test ordering levels by name."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        # Test ascending order (default)
        response = self.client.get(self.levels_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [level["name"] for level in response.data]
        self.assertEqual(names, sorted(names))
        
        # Test descending order
        response = self.client.get(f"{self.levels_url}?ordering=-name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [level["name"] for level in response.data]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_levels_pagination(self):
        """Test pagination of levels."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        # Create more levels to test pagination
        for i in range(15):
            Level.objects.create(
                skill=self.python_skill,
                name=f"Extra Level {i}",
                order=i+3,
                description=f"Description for level {i}"
            )
        
        response = self.client.get(f"{self.levels_url}?page=1&page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 17)  # 2 original + 15 new levels

    # LEVEL DETAIL TESTS
    def test_level_detail_access_denied_without_auth(self):
        """Test that unauthenticated users are denied access to level details."""
        response = self.client.get(self.level_url(self.beginner_level.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_level_detail_no_permission(self):
        """Test that users without view_level permission cannot access level details."""
        self.authenticate(
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"]
        )
        response = self.client.get(self.level_url(self.beginner_level.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_level_detail_with_permission(self):
        """Test that users with view_level permission can access level details."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.level_url(self.beginner_level.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Beginner")
        self.assertEqual(response.data["order"], 1)
        self.assertEqual(response.data["description"], "Basic Python knowledge")

    def test_level_not_found(self):
        """Test proper handling of non-existent level IDs."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.level_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Level not found.")

    # LEVEL CREATION TESTS
    def test_create_level_access_denied_without_auth(self):
        """Test that unauthenticated users cannot create levels."""
        response = self.client.post(self.levels_url, self.new_level_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_level_no_permission(self):
        """Test that users without create_level permission cannot create levels."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.post(self.levels_url, self.new_level_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to create levels."
        )

    def test_create_level_with_permission(self):
        """Test that users with create_level permission can create levels."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        response = self.client.post(self.levels_url, self.new_level_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Beginner")
        self.assertEqual(response.data["order"], 1)
        self.assertEqual(response.data["description"], "Basic JavaScript knowledge")

    # LEVEL VALIDATION TESTS
    def test_create_level_validation_errors(self):
        """Test validation errors when creating a level."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        
        # Test short name
        invalid_data = self.new_level_data.copy()
        invalid_data["name"] = "A"
        response = self.client.post(self.levels_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Level name must be at least 2 characters long.")
        
        # Test duplicate order for same skill
        invalid_data = self.new_level_data.copy()
        invalid_data["skill_id"] = self.python_skill.id
        invalid_data["order"] = 1  # Already exists for python skill
        response = self.client.post(self.levels_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order", response.data)
        self.assertEqual(response.data["order"][0], "A level with order 1 already exists for this skill.")

    def test_level_name_blank(self):
        """Test validation for blank level name."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_level_data.copy()
        data["name"] = ""
        
        response = self.client.post(self.levels_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Level name is required.")

    def test_level_name_whitespace(self):
        """Test that leading/trailing whitespace in level name is stripped."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_level_data.copy()
        data["name"] = "  Advanced  "
        data["order"] = 2  # Different from existing orders
        
        response = self.client.post(self.levels_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Advanced")

    def test_level_name_max_length(self):
        """Test that level name cannot exceed maximum length."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_level_data.copy()
        data["name"] = "A" * 101  # Max length is 100
        
        response = self.client.post(self.levels_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Level name cannot exceed 100 characters.")

    def test_level_order_validation(self):
        """Test that level order must be a positive integer."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_level_data.copy()
        data["order"] = 0  # Should be positive
        
        response = self.client.post(self.levels_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order", response.data)
        self.assertEqual(response.data["order"][0], "Level order must be a positive integer.")

    # LEVEL UPDATE TESTS
    def test_update_level_access_denied_without_auth(self):
        """Test that unauthenticated users cannot update levels."""
        update_data = {"name": "Updated Level", "description": "Updated description", "order": 1}
        response = self.client.put(self.level_url(self.beginner_level.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_level_no_permission(self):
        """Test that users without update_level permission cannot update levels."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        update_data = {"name": "Updated Level", "description": "Updated description", "order": 1}
        response = self.client.put(self.level_url(self.beginner_level.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to update levels."
        )

    def test_update_level_with_permission(self):
        """Test that users with update_level permission can update levels."""
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"]
        )
        update_data = {
            "skill_id": self.python_skill.id,
            "name": "Basic",
            "order": 1,
            "description": "Updated beginner level description"
        }
        response = self.client.put(self.level_url(self.beginner_level.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Basic")
        self.assertEqual(response.data["description"], "Updated beginner level description")

    def test_partial_update_level(self):
        """Test partial update of a level."""
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"]
        )
        # Update only the name
        update_data = {"name": "Python Basics"}
        response = self.client.patch(self.level_url(self.beginner_level.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Python Basics")
        self.assertEqual(response.data["order"], 1)  # Unchanged
        self.assertEqual(response.data["description"], "Basic Python knowledge")  # Unchanged

    # LEVEL DELETION TESTS
    def test_delete_level_access_denied_without_auth(self):
        """Test that unauthenticated users cannot delete levels."""
        response = self.client.delete(self.level_url(self.beginner_level.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_level_no_permission(self):
        """Test that users without delete_level permission cannot delete levels."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.delete(self.level_url(self.beginner_level.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to delete levels."
        )

    def test_delete_level_with_permission(self):
        """Test that users with delete_level permission can delete levels."""
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"]
        )
        response = self.client.delete(self.level_url(self.beginner_level.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify level is deleted
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.level_url(self.beginner_level.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_level(self):
        """Test deleting a non-existent level."""
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"]
        )
        response = self.client.delete(self.level_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Level not found.")

    # SERIALIZER TESTS
    def test_level_serializer(self):
        """Test that LevelSerializer works correctly."""
        serializer = LevelSerializer(self.beginner_level)
        data = serializer.data
        
        # Check all fields are present
        expected_fields = {"id", "skill_id", "name", "order", "description", "created_at", "updated_at"}
        self.assertEqual(set(data.keys()), expected_fields)
        
        # Check values
        self.assertEqual(data["name"], self.beginner_level.name)
        self.assertEqual(data["order"], self.beginner_level.order)
        self.assertEqual(data["description"], self.beginner_level.description)
        self.assertEqual(data["skill_id"], self.python_skill.id)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])