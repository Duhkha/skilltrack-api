from django.contrib import admin
from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_lead', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'