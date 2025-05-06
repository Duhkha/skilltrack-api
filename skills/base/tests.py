from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from skills.models import Skill
from users.models import User
from permissions.models import Permission, PermissionGroup
from roles.models import Role
from .serializers import SkillSerializer


class SkillTests(APITestCase):
    def setUp(self):
        # Create permission groups
        self.skills_permission_group = PermissionGroup.objects.create(
            name="skills", description="Permissions related to skill management."
        )

        # Create skill permissions
        self.view_skill_permission = Permission.objects.create(
            name="view_skill",
            description="Permission to view skills.",
            group=self.skills_permission_group,
        )
        self.create_skill_permission = Permission.objects.create(
            name="create_skill",
            description="Permission to create a new skill.",
            group=self.skills_permission_group,
        )
        self.update_skill_permission = Permission.objects.create(
            name="update_skill",
            description="Permission to update an existing skill.",
            group=self.skills_permission_group,
        )
        self.delete_skill_permission = Permission.objects.create(
            name="delete_skill",
            description="Permission to delete a skill.",
            group=self.skills_permission_group,
        )
        
        # Create roles with different permissions
        self.admin_role = Role.objects.create(name="admin")
        self.view_role = Role.objects.create(name="viewer")
        self.create_role = Role.objects.create(name="creator")
        self.update_role = Role.objects.create(name="updater")
        self.delete_role = Role.objects.create(name="deleter")
        
        # Assign permissions to roles
        self.admin_role.permissions.set([
            self.view_skill_permission,
            self.create_skill_permission,
            self.update_skill_permission,
            self.delete_skill_permission
        ])
        self.view_role.permissions.set([self.view_skill_permission])
        self.create_role.permissions.set([self.create_skill_permission])
        self.update_role.permissions.set([self.update_skill_permission])
        self.delete_role.permissions.set([self.delete_skill_permission])
        
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
        self.python_skill_data = {
            "name": "Python",
            "description": "Programming language"
        }
        self.javascript_skill_data = {
            "name": "JavaScript",
            "description": "Web programming language"
        }
        self.new_skill_data = {
            "name": "React",
            "description": "JavaScript library for building user interfaces"
        }
        
        self.python_skill = Skill.objects.create(
            name=self.python_skill_data["name"],
            description=self.python_skill_data["description"]
        )
        
        self.javascript_skill = Skill.objects.create(
            name=self.javascript_skill_data["name"],
            description=self.javascript_skill_data["description"]
        )
        
        # Define URLs
        self.sign_in_url = reverse("sign-in")
        self.skills_url = reverse("skill-list")
        self.skill_url = lambda skill_id: reverse("skill-detail", args=[skill_id])

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
    def test_skills_access_denied_without_auth(self):
        """Test that unauthenticated users are denied access to skills."""
        response = self.client.get(self.skills_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_skills_no_permission(self):
        """Test that authenticated users without view_skill permission cannot get skills."""
        self.authenticate(
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"]
        )
        response = self.client.get(self.skills_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to view skills."
        )

    # SKILL LISTING AND FILTERING TESTS
    def test_skills_with_permission(self):
        """Test that users with view_skill permission can get all skills."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.skills_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two skills in the setup
        
        # Verify response structure
        skill = response.data[0]
        self.assertIn("id", skill)
        self.assertIn("name", skill)
        self.assertIn("description", skill)
        self.assertIn("created_at", skill)
        self.assertIn("updated_at", skill)

    def test_skills_search_by_name(self):
        """Test searching skills by name."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(f"{self.skills_url}?search=python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Python")

    def test_skills_search_by_description(self):
        """Test searching skills by description."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(f"{self.skills_url}?search=web")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "JavaScript")

    def test_skills_ordering(self):
        """Test ordering skills by name."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        # Test ascending order (default)
        response = self.client.get(self.skills_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [skill["name"] for skill in response.data]
        self.assertEqual(names, sorted(names))
        
        # Test descending order
        response = self.client.get(f"{self.skills_url}?ordering=-name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [skill["name"] for skill in response.data]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_skills_pagination(self):
        """Test pagination of skills."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        # Create more skills to test pagination
        for i in range(15):
            Skill.objects.create(
                name=f"Extra Skill {i}",
                description=f"Description for skill {i}"
            )
        
        response = self.client.get(f"{self.skills_url}?page=1&page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 17)  # 2 original + 15 new skills

    # SKILL DETAIL TESTS
    def test_skill_detail_access_denied_without_auth(self):
        """Test that unauthenticated users are denied access to skill details."""
        response = self.client.get(self.skill_url(self.python_skill.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_skill_detail_no_permission(self):
        """Test that users without view_skill permission cannot access skill details."""
        self.authenticate(
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"]
        )
        response = self.client.get(self.skill_url(self.python_skill.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_skill_detail_with_permission(self):
        """Test that users with view_skill permission can access skill details."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.skill_url(self.python_skill.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Python")
        self.assertEqual(response.data["description"], "Programming language")

    def test_skill_not_found(self):
        """Test proper handling of non-existent skill IDs."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.skill_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Skill not found.")

    # SKILL CREATION TESTS
    def test_create_skill_access_denied_without_auth(self):
        """Test that unauthenticated users cannot create skills."""
        response = self.client.post(self.skills_url, self.new_skill_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_skill_no_permission(self):
        """Test that users without create_skill permission cannot create skills."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.post(self.skills_url, self.new_skill_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to create skills."
        )

    def test_create_skill_with_permission(self):
        """Test that users with create_skill permission can create skills."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        response = self.client.post(self.skills_url, self.new_skill_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "React")
        self.assertEqual(response.data["description"], "JavaScript library for building user interfaces")

    # SKILL VALIDATION TESTS
    def test_create_skill_validation_errors(self):
        """Test validation errors when creating a skill."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        
        # Test short name
        invalid_data = self.new_skill_data.copy()
        invalid_data["name"] = "A"
        response = self.client.post(self.skills_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Skill name must be at least 2 characters long.")
        
        # Test duplicate name
        invalid_data = self.new_skill_data.copy()
        invalid_data["name"] = "Python"
        response = self.client.post(self.skills_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Skill with this name already exists.")

    def test_skill_name_blank(self):
        """Test validation for blank skill name."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_skill_data.copy()
        data["name"] = ""
        
        response = self.client.post(self.skills_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Skill name is required.")

    def test_skill_name_whitespace(self):
        """Test that leading/trailing whitespace in skill name is stripped."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_skill_data.copy()
        data["name"] = "  Django  "
        
        response = self.client.post(self.skills_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Django")

    def test_skill_name_max_length(self):
        """Test that skill name cannot exceed maximum length."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_skill_data.copy()
        data["name"] = "A" * 101  # Max length is 100
        
        response = self.client.post(self.skills_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Skill name cannot exceed 100 characters.")

    # SKILL UPDATE TESTS
    def test_update_skill_access_denied_without_auth(self):
        """Test that unauthenticated users cannot update skills."""
        update_data = {"name": "Updated Skill", "description": "Updated description"}
        response = self.client.put(self.skill_url(self.python_skill.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_skill_no_permission(self):
        """Test that users without update_skill permission cannot update skills."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        update_data = {"name": "Updated Skill", "description": "Updated description"}
        response = self.client.put(self.skill_url(self.python_skill.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to update skills."
        )

    def test_update_skill_with_permission(self):
        """Test that users with update_skill permission can update skills."""
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"]
        )
        update_data = {
            "name": "Python 3",
            "description": "Updated programming language description"
        }
        response = self.client.put(self.skill_url(self.python_skill.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Python 3")
        self.assertEqual(response.data["description"], "Updated programming language description")

    def test_partial_update_skill(self):
        """Test partial update of a skill."""
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"]
        )
        # Update only the name
        update_data = {"name": "Python 3.9"}
        response = self.client.patch(self.skill_url(self.python_skill.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Python 3.9")
        self.assertEqual(response.data["description"], "Programming language")

    # SKILL DELETION TESTS
    def test_delete_skill_access_denied_without_auth(self):
        """Test that unauthenticated users cannot delete skills."""
        response = self.client.delete(self.skill_url(self.python_skill.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_skill_no_permission(self):
        """Test that users without delete_skill permission cannot delete skills."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.delete(self.skill_url(self.python_skill.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to delete skills."
        )

    def test_delete_skill_with_permission(self):
        """Test that users with delete_skill permission can delete skills."""
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"]
        )
        response = self.client.delete(self.skill_url(self.python_skill.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify skill is deleted
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.skill_url(self.python_skill.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_skill(self):
        """Test deleting a non-existent skill."""
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"]
        )
        response = self.client.delete(self.skill_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Skill not found.")

    # SERIALIZER TESTS
    def test_skill_serializer(self):
        """Test that SkillSerializer works correctly."""
        serializer = SkillSerializer(self.python_skill)
        data = serializer.data
        
        # Check all fields are present
        self.assertEqual(set(data.keys()), {"id", "name", "description", "created_at", "updated_at"})
        
        # Check values
        self.assertEqual(data["name"], self.python_skill.name)
        self.assertEqual(data["description"], self.python_skill.description)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])