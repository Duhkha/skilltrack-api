from django.core.management.base import BaseCommand
from permissions.models import PermissionGroup, Permission


class Command(BaseCommand):
    help = "Seed initial permission groups and permissions."

    def handle(self, *args, **kwargs):
        verbosity = kwargs.get("verbosity", 1)

        roles_permission_group, created = PermissionGroup.objects.get_or_create(
            name="roles",
            defaults={"description": "Permissions related to role management."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: roles.")
                )

        permission_data = [
            (
                "view_role",
                "Permission to view roles, including listing all roles and retrieving individual role details.",
            ),
            ("create_role", "Permission to create a new role."),
            ("update_role", "Permission to update an existing role."),
            ("delete_role", "Permission to delete a role."),
        ]

        for name, description in permission_data:
            _, created = Permission.objects.get_or_create(
                group=roles_permission_group,
                name=name,
                defaults={"description": description},
            )
            if created:
                if verbosity >= 1:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created permission: {name}.")
                    )
                if verbosity >= 2:
                    self.stdout.write(
                        f"Permission {name} created with description: {description}."
                    )

        users_permission_group, created = PermissionGroup.objects.get_or_create(
            name="users",
            defaults={"description": "Permissions related to user management."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: users.")
                )

        user_permissions_data = [
            (
                "view_user",
                "Permission to view users, including listing all users and retrieving individual user details.",
            ),
            ("create_user", "Permission to create a new user."),
            ("update_user", "Permission to update an existing user."),
            ("delete_user", "Permission to delete a user."),
        ]

        for name, description in user_permissions_data:
            _, created = Permission.objects.get_or_create(
                group=users_permission_group,
                name=name,
                defaults={"description": description},
            )
            if created:
                if verbosity >= 1:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created permission: {name}.")
                    )
                if verbosity >= 2:
                    self.stdout.write(
                        f"Permission {name} created with description: {description}."
                    )
        
        teams_permission_group, created = PermissionGroup.objects.get_or_create(
            name="teams",
            defaults={"description": "Permissions related to team management."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: teams.")
                )

        # Team permissions
        team_permissions_data = [
            (
                "view_team",
                "Permission to view teams, including listing all teams and retrieving individual team details.",
            ),
            (
                "create_team",
                "Permission to create a new team.",
            ),
            (
                "update_team",
                "Permission to update an existing team.",
            ),
            (
                "delete_team",
                "Permission to delete a team.",
            ),
            (
                "manage_team_members",
                "Permission to add or remove members from teams.",
            ),
        ]

        for name, description in team_permissions_data:
            _, created = Permission.objects.get_or_create(
                group=teams_permission_group,
                name=name,
                defaults={"description": description},
            )
            if created:
                if verbosity >= 1:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created permission: {name}.")
                    )
                if verbosity >= 2:
                    self.stdout.write(
                        f"Permission {name} created with description: {description}."
                    )
        
                # Create skills permission group
        skills_permission_group, created = PermissionGroup.objects.get_or_create(
            name="skills",
            defaults={"description": "Permissions related to skill management."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: skills.")
                )

        # Skill permissions
        skill_permissions_data = [
            (
                "view_skill",
                "Permission to view skills, including listing all skills and retrieving individual skill details.",
            ),
            (
                "create_skill", 
                "Permission to create a new skill."
            ),
            (
                "update_skill",
                "Permission to update an existing skill.",
            ),
            (
                "delete_skill",
                "Permission to delete a skill.",
            ),
        ]

        for name, description in skill_permissions_data:
            _, created = Permission.objects.get_or_create(
                group=skills_permission_group,
                name=name,
                defaults={"description": description},
            )
            if created:
                if verbosity >= 1:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created permission: {name}.")
                    )
                if verbosity >= 2:
                    self.stdout.write(
                        f"Permission {name} created with description: {description}."
                    )
