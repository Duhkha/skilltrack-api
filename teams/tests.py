from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from .models import Team

class TeamModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(name="testuser", email="test@example.com")
        self.team = Team.objects.create(
            name="Test Team",
            description="Test Description",
            team_lead=self.user
        )
        self.team.members.add(self.user)

    def test_team_creation(self):
        self.assertEqual(self.team.name, "Test Team")
        self.assertEqual(self.team.team_lead, self.user)
        self.assertEqual(self.team.members.count(), 1)