from django.db import models
from accounts.models import User

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='teams_member_of')
    team_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teams_lead_of')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    # Helper methods
    def get_members(self):
        return self.members.all()
    
    def get_lead(self):
        return self.team_lead