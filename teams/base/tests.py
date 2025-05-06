from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from teams.models import Team
from users.models import User
from permissions.models import Permission, PermissionGroup
from roles.models import Role
from .serializers import SimpleUserSerializer, TeamSerializer, TeamDetailSerializer


class TeamTests(APITestCase):
    def setUp(self):
        # Create permission groups
        self.teams_permission_group = PermissionGroup.objects.create(
            name="teams", description="Permissions related to team management."
        )
        self.users_permission_group = PermissionGroup.objects.create(
            name="users", description="Permissions related to user management."
        )

        # Create team permissions
        self.view_team_permission = Permission.objects.create(
            name="view_team",
            description="Permission to view teams.",
            group=self.teams_permission_group,
        )
        self.create_team_permission = Permission.objects.create(
            name="create_team",
            description="Permission to create a new team.",
            group=self.teams_permission_group,
        )
        self.update_team_permission = Permission.objects.create(
            name="update_team",
            description="Permission to update an existing team.",
            group=self.teams_permission_group,
        )
        self.delete_team_permission = Permission.objects.create(
            name="delete_team",
            description="Permission to delete a team.",
            group=self.teams_permission_group,
        )
        
        # Create user permissions
        self.view_user_permission = Permission.objects.create(
            name="view_user",
            description="Permission to view users.",
            group=self.users_permission_group,
        )
        
        # Create roles with different permissions
        self.admin_role = Role.objects.create(name="admin")
        self.view_role = Role.objects.create(name="viewer")
        self.create_role = Role.objects.create(name="creator")
        self.update_role = Role.objects.create(name="updater")
        self.delete_role = Role.objects.create(name="deleter")
        
        # Assign permissions to roles
        self.admin_role.permissions.set([
            self.view_team_permission,
            self.create_team_permission,
            self.update_team_permission,
            self.delete_team_permission,
            self.view_user_permission
        ])
        self.view_role.permissions.set([self.view_team_permission, self.view_user_permission])
        self.create_role.permissions.set([self.create_team_permission, self.view_user_permission])
        self.update_role.permissions.set([self.update_team_permission, self.view_user_permission])
        self.delete_role.permissions.set([self.delete_team_permission, self.view_user_permission])
        
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
        
        # Create test teams
        self.engineering_team_data = {
            "name": "Engineering Team",
            "description": "Software development team"
        }
        self.marketing_team_data = {
            "name": "Marketing Team",
            "description": "Marketing and communications"
        }
        self.new_team_data = {
            "name": "New Team",
            "description": "A new test team",
            "team_lead_id": self.view_user.id,
            "member_ids": [self.create_user.id, self.update_user.id]
        }
        
        self.engineering_team = Team.objects.create(
            name=self.engineering_team_data["name"],
            description=self.engineering_team_data["description"],
            team_lead=self.update_user
        )
        self.engineering_team.members.add(self.view_user, self.create_user)
        
        self.marketing_team = Team.objects.create(
            name=self.marketing_team_data["name"],
            description=self.marketing_team_data["description"],
            team_lead=self.admin_user
        )
        self.marketing_team.members.add(self.delete_user, self.regular_user)
        
        # Define URLs
        self.sign_in_url = reverse("sign-in")
        self.teams_url = reverse("team-list")
        self.team_url = lambda team_id: reverse("team-detail", args=[team_id])

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
    def test_teams_access_denied_without_auth(self):
        """Test that unauthenticated users are denied access to teams."""
        response = self.client.get(self.teams_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_teams_no_permission(self):
        """Test that authenticated users without view_team permission cannot get teams."""
        self.authenticate(
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"]
        )
        response = self.client.get(self.teams_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to view teams."
        )

    # TEAM LISTING AND FILTERING TESTS
    def test_teams_with_permission(self):
        """Test that users with view_team permission can get all teams."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.teams_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two teams in the setup
        
        # Verify response structure
        team = response.data[0]
        self.assertIn("id", team)
        self.assertIn("name", team)
        self.assertIn("description", team)
        self.assertIn("team_lead", team)
        self.assertIn("members", team)

    def test_teams_search_by_name(self):
        """Test searching teams by name."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(f"{self.teams_url}?search=engineering")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Engineering Team")

    def test_teams_search_by_description(self):
        """Test searching teams by description."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(f"{self.teams_url}?search=marketing")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Marketing Team")

    def test_teams_ordering(self):
        """Test ordering teams by name."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        # Test ascending order
        response = self.client.get(f"{self.teams_url}?ordering=name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [team["name"] for team in response.data]
        self.assertEqual(names, sorted(names))
        
        # Test descending order
        response = self.client.get(f"{self.teams_url}?ordering=-name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [team["name"] for team in response.data]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_teams_pagination(self):
        """Test pagination of teams."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        # Create more teams to test pagination
        for i in range(5):
            team = Team.objects.create(
                name=f"Extra Team {i}",
                description=f"Description for team {i}",
                team_lead=self.update_user
            )
            team.members.add(self.view_user)
        
        response = self.client.get(f"{self.teams_url}?page=1&page_size=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["count"], 7)  # 2 original + 5 new teams

    # TEAM DETAIL TESTS
    def test_team_detail_access_denied_without_auth(self):
        """Test that unauthenticated users are denied access to team details."""
        response = self.client.get(self.team_url(self.engineering_team.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_detail_no_permission(self):
        """Test that users without view_team permission cannot access team details."""
        self.authenticate(
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"]
        )
        response = self.client.get(self.team_url(self.engineering_team.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_detail_with_permission(self):
        """Test that users with view_team permission can access team details."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.team_url(self.engineering_team.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Engineering Team")
        self.assertEqual(response.data["description"], "Software development team")
        self.assertEqual(response.data["team_lead"]["id"], self.update_user.id)
        self.assertEqual(len(response.data["members"]), 2)
        
        # Check that detailed member info is included
        self.assertIn("email", response.data["team_lead"])
        self.assertIn("email", response.data["members"][0])
        self.assertIn("member_count", response.data)
        self.assertEqual(response.data["member_count"], 2)

    def test_team_not_found(self):
        """Test proper handling of non-existent team IDs."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.get(self.team_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Team not found.")

    # TEAM CREATION TESTS
    def test_create_team_access_denied_without_auth(self):
        """Test that unauthenticated users cannot create teams."""
        response = self.client.post(self.teams_url, self.new_team_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_team_no_permission(self):
        """Test that users without create_team permission cannot create teams."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.post(self.teams_url, self.new_team_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to create teams."
        )

    def test_create_team_with_permission(self):
        """Test that users with create_team permission can create teams."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        response = self.client.post(self.teams_url, self.new_team_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Team")
        self.assertEqual(response.data["description"], "A new test team")
        self.assertEqual(response.data["team_lead"]["id"], self.view_user.id)
        self.assertEqual(len(response.data["members"]), 2)

    def test_create_team_without_lead(self):
        """Test creating a team without a lead."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_team_data.copy()
        data["team_lead_id"] = None
        
        response = self.client.post(self.teams_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["team_lead"])
        self.assertEqual(len(response.data["members"]), 2)

    def test_create_team_without_members(self):
        """Test creating a team without members."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_team_data.copy()
        data["member_ids"] = []
        
        response = self.client.post(self.teams_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["team_lead"]["id"], self.view_user.id)
        self.assertEqual(len(response.data["members"]), 0)

    # TEAM VALIDATION TESTS
    def test_create_team_validation_errors(self):
        """Test validation errors when creating a team."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        
        # Test short name
        invalid_data = self.new_team_data.copy()
        invalid_data["name"] = "AB"
        response = self.client.post(self.teams_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Team name must be at least 3 characters long.")
        
        # Test duplicate name
        invalid_data = self.new_team_data.copy()
        invalid_data["name"] = "Engineering Team"
        response = self.client.post(self.teams_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Team with this name already exists.")
        
        # Test duplicate members
        invalid_data = self.new_team_data.copy()
        invalid_data["member_ids"] = [self.create_user.id, self.create_user.id]
        response = self.client.post(self.teams_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member_ids", response.data)
        self.assertTrue("Duplicate members found" in response.data["member_ids"][0])
        
        # Test team lead as member
        invalid_data = self.new_team_data.copy()
        invalid_data["team_lead_id"] = self.view_user.id
        invalid_data["member_ids"] = [self.view_user.id, self.create_user.id]
        response = self.client.post(self.teams_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member_ids", response.data)
        self.assertTrue("should not be included in the members list" in response.data["member_ids"][0])

    def test_team_name_blank(self):
        """Test validation for blank team name."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_team_data.copy()
        data["name"] = ""
        
        response = self.client.post(self.teams_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"][0], "Team name is required.")

    def test_team_name_whitespace(self):
        """Test that leading/trailing whitespace in team name is stripped."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_team_data.copy()
        data["name"] = "  Padded Team Name  "
        
        response = self.client.post(self.teams_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Padded Team Name")

    def test_team_name_max_length(self):
        """Test that team name cannot exceed maximum length."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        data = self.new_team_data.copy()
        data["name"] = "A" * 101  # Assuming max length is 100
        
        response = self.client.post(self.teams_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertTrue("exceed" in response.data["name"][0].lower())

    def test_invalid_user_ids(self):
        """Test handling of invalid user IDs in team creation."""
        self.authenticate(
            email=self.create_user_data["email"],
            password=self.create_user_data["password"]
        )
        
        # Test invalid team lead ID
        invalid_data = self.new_team_data.copy()
        invalid_data["team_lead_id"] = 99999
        response = self.client.post(self.teams_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_lead_id", response.data)
        
        # Test invalid member ID
        invalid_data = self.new_team_data.copy()
        invalid_data["member_ids"] = [99999]
        response = self.client.post(self.teams_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("member_ids", response.data)

    # TEAM UPDATE TESTS
    def test_update_team_access_denied_without_auth(self):
        """Test that unauthenticated users cannot update teams."""
        update_data = {"name": "Updated Team", "description": "Updated description"}
        response = self.client.put(self.team_url(self.engineering_team.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_team_no_permission(self):
        """Test that users without update_team permission cannot update teams."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        update_data = {"name": "Updated Team", "description": "Updated description"}
        response = self.client.put(self.team_url(self.engineering_team.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_team_with_permission(self):
        """Test that users with update_team permission can update teams."""
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"]
        )
        update_data = {
            "name": "Updated Engineering Team",
            "description": "Updated software development team",
            "team_lead_id": self.create_user.id,
            "member_ids": [self.view_user.id, self.delete_user.id]
        }
        response = self.client.put(self.team_url(self.engineering_team.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Engineering Team")
        self.assertEqual(response.data["description"], "Updated software development team")
        self.assertEqual(response.data["team_lead"]["id"], self.create_user.id)
        self.assertEqual(len(response.data["members"]), 2)

    def test_partial_update_team(self):
        """Test partial update of a team."""
        self.authenticate(
            email=self.update_user_data["email"],
            password=self.update_user_data["password"]
        )
        # Update only the name
        update_data = {"name": "Partially Updated Team"}
        response = self.client.patch(self.team_url(self.engineering_team.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Partially Updated Team")
        self.assertEqual(response.data["description"], "Software development team")
        self.assertEqual(response.data["team_lead"]["id"], self.update_user.id)

    def test_team_lead_can_update_own_team(self):
        """Test that team lead can update their team even without update_team permission."""
        # Create a team with regular user as lead (who has no update_team permission)
        team = Team.objects.create(
            name="Regular User's Team",
            description="Team led by user without update permission",
            team_lead=self.regular_user
        )
        team.members.add(self.view_user)
        
        self.authenticate(
            email=self.regular_user_data["email"],
            password=self.regular_user_data["password"]
        )
        
        update_data = {
            "name": "Updated By Lead",
            "description": "Team updated by its lead",
            "team_lead_id": self.regular_user.id,
            "member_ids": [self.view_user.id, self.create_user.id]
        }
        
        response = self.client.put(self.team_url(team.id), update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated By Lead")
        self.assertEqual(len(response.data["members"]), 2)

    # TEAM DELETION TESTS
    def test_delete_team_access_denied_without_auth(self):
        """Test that unauthenticated users cannot delete teams."""
        response = self.client.delete(self.team_url(self.engineering_team.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_team_no_permission(self):
        """Test that users without delete_team permission cannot delete teams."""
        self.authenticate(
            email=self.view_user_data["email"],
            password=self.view_user_data["password"]
        )
        response = self.client.delete(self.team_url(self.engineering_team.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to delete teams."
        )

    def test_delete_team_with_permission(self):
        """Test that users with delete_team permission can delete teams."""
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"]
        )
        response = self.client.delete(self.team_url(self.engineering_team.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify team is deleted
        response = self.client.get(self.team_url(self.engineering_team.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_team(self):
        """Test deleting a non-existent team."""
        self.authenticate(
            email=self.delete_user_data["email"],
            password=self.delete_user_data["password"]
        )
        response = self.client.delete(self.team_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Team not found.")

    # SERIALIZER TESTS
    def test_simple_user_serializer(self):
        """Test that SimpleUserSerializer returns only id and name"""
        serializer = SimpleUserSerializer(self.admin_user)
        self.assertEqual(set(serializer.data.keys()), {"id", "name"})
        self.assertEqual(serializer.data["name"], self.admin_user.name)
        self.assertEqual(serializer.data["id"], self.admin_user.id)

    def test_team_serializer_read(self):
        """Test TeamSerializer for reading data"""
        serializer = TeamSerializer(self.engineering_team)
        data = serializer.data
        
        self.assertEqual(data["name"], self.engineering_team.name)
        self.assertEqual(data["description"], self.engineering_team.description)
        self.assertEqual(data["team_lead"]["id"], self.update_user.id)
        self.assertEqual(len(data["members"]), 2)
        
        # Verify members are serialized correctly
        member_ids = [member["id"] for member in data["members"]]
        self.assertIn(self.view_user.id, member_ids)
        self.assertIn(self.create_user.id, member_ids)

    def test_team_detail_serializer(self):
        """Test TeamDetailSerializer with expanded user data"""
        serializer = TeamDetailSerializer(self.engineering_team)
        data = serializer.data
        
        # Check correct fields are present
        self.assertEqual(data["name"], self.engineering_team.name)
        self.assertEqual(data["description"], self.engineering_team.description)
        
        # Check team lead is fully serialized
        self.assertEqual(data["team_lead"]["id"], self.update_user.id)
        self.assertEqual(data["team_lead"]["name"], self.update_user.name)
        self.assertIn("email", data["team_lead"])  # UserSerializer includes email
        
        # Check members are fully serialized
        self.assertEqual(len(data["members"]), 2)
        self.assertIn("email", data["members"][0])
        
        # Check member count
        self.assertEqual(data["member_count"], 2)