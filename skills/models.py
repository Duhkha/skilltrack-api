from django.db import models
from django.conf import settings

class Skill(models.Model):
    """
    Model for skills that can be assigned to users
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Level(models.Model):
    """
    Model for skill levels where each skill can have multiple levels
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['skill', 'order']
        unique_together = ['skill', 'order']
    
    def __str__(self):
        return f"{self.skill.name} - Level {self.order}: {self.name}"


class Expectation(models.Model):
    """
    Model for defining requirements to complete a level
    """
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='expectations')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Expectation for {self.level}: {self.description[:50]}..."


class UserSkill(models.Model):
    """
    Model for tracking which level a user has achieved in each skill
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    current_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='user_skills')
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'skill')  # Ensures user can have only one level per skill
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.name} (Level: {self.current_level.name})"


class UserExpectationProgress(models.Model):
    """
    Model for tracking user progress on expectations
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('completed', 'Completed'),
        ('approved', 'Approved')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expectation_progress')
    expectation = models.ForeignKey(Expectation, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='approved_expectations',
        null=True, 
        blank=True
    )
    
    class Meta:
        unique_together = ('user', 'expectation')
    
    def __str__(self):
        return f"{self.user.username} - {self.expectation} ({self.get_status_display()})"