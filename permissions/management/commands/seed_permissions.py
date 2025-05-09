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
        
        # Create levels permission group
        levels_permission_group, created = PermissionGroup.objects.get_or_create(
            name="levels",
            defaults={"description": "Permissions related to level management."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: levels.")
                )

        # Level permissions
        level_permissions_data = [
            (
                "view_level",
                "Permission to view levels, including listing all levels and retrieving individual level details.",
            ),
            (
                "create_level", 
                "Permission to create a new level."
            ),
            (
                "update_level",
                "Permission to update an existing level.",
            ),
            (
                "delete_level",
                "Permission to delete a level.",
            ),
        ]

        for name, description in level_permissions_data:
            _, created = Permission.objects.get_or_create(
                group=levels_permission_group,
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
        
                # Create expectations permission group
        expectations_permission_group, created = PermissionGroup.objects.get_or_create(
            name="expectations",
            defaults={"description": "Permissions related to skill level expectations."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: expectations.")
                )

        # Expectations permissions
        expectation_permissions_data = [
            (
                "view_expectation",
                "Permission to view expectations for skill levels.",
            ),
            (
                "create_expectation", 
                "Permission to create new expectations for levels."
            ),
            (
                "update_expectation",
                "Permission to update existing expectations.",
            ),
            (
                "delete_expectation",
                "Permission to delete expectations.",
            ),
        ]

        for name, description in expectation_permissions_data:
            _, created = Permission.objects.get_or_create(
                group=expectations_permission_group,
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
        
        # Create user skills permission group
        user_skills_permission_group, created = PermissionGroup.objects.get_or_create(
            name="user_skills",
            defaults={"description": "Permissions related to user skill assignments."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: user_skills.")
                )

        # User skill permissions
        user_skill_permissions_data = [
            (
                "view_user_skill",
                "Permission to view which skills and levels are assigned to users.",
            ),
            (
                "create_user_skill", 
                "Permission to assign skills and levels to users."
            ),
            (
                "update_user_skill",
                "Permission to update a user's skill level.",
            ),
            (
                "delete_user_skill",
                "Permission to remove skill assignments from users.",
            ),
        ]

        for name, description in user_skill_permissions_data:
            _, created = Permission.objects.get_or_create(
                group=user_skills_permission_group,
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
        
        # Create expectation progress permission group
        expectation_progress_permission_group, created = PermissionGroup.objects.get_or_create(
            name="expectation_progress",
            defaults={"description": "Permissions related to tracking and approving user progress on expectations."},
        )
        if created:
            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS("Created permission group: expectation_progress.")
                )

        # Expectation progress permissions
        expectation_progress_permissions_data = [
            (
                "view_expectation_progress",
                "Permission to view user progress on expectations.",
            ),
            (
                "create_expectation_progress", 
                "Permission to create progress records for users."
            ),
            (
                "update_expectation_progress",
                "Permission to update user progress status.",
            ),
            (
                "delete_expectation_progress",
                "Permission to delete progress records.",
            ),
            (
                "approve_expectation",
                "Permission to approve completed expectations and advance users to next level.",
            ),
        ]

        for name, description in expectation_progress_permissions_data:
            _, created = Permission.objects.get_or_create(
                group=expectation_progress_permission_group,
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
