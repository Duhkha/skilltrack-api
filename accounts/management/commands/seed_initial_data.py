from django.core.management.base import BaseCommand

from accounts.models import Permission, PermissionGroup, Role, User


class Command(BaseCommand):
    help = "Seed initial permission groups, permissions, roles, and an admin user."

    def handle(self, *args, **kwargs):
        roles_group, created = PermissionGroup.objects.get_or_create(
            name="roles",
            defaults={"description": "Permissions related to role management."},
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created permission group: roles"))

        permission_data = [
            (
                "view_role",
                "Permission to view roles, including listing all roles and retrieving individual role details.",
            ),
            ("create_role", "Permission to create a new role."),
            ("update_role", "Permission to update an existing role."),
            ("delete_role", "Permission to delete a role."),
        ]

        permissions = []

        for permission_name, description in permission_data:
            permission, created = Permission.objects.get_or_create(
                group=roles_group,
                name=permission_name,
                defaults={"description": description},
            )
            permissions.append(permission)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created permission: {permission_name}")
                )

        admin_role, created = Role.objects.get_or_create(name="admin")
        all_permissions = Permission.objects.all()
        admin_role.permissions.set(all_permissions)
        admin_role.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Created role: admin"))
        else:
            self.stdout.write("Admin role already exists. Permissions were updated.")

        admin_email = "admin@example.com"
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_user(
                name="Admin",
                email=admin_email,
                password="Admin123!",
                role=admin_role,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_email}"))
        else:
            self.stdout.write(f"Admin user already exists: {admin_email}")
