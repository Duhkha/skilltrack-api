from django.core.management.base import BaseCommand
from permissions.models import Permission
from roles.models import Role


class Command(BaseCommand):
    help = "Seed roles and assign permissions."

    def handle(self, *args, **kwargs):
        verbosity = kwargs.get("verbosity", 1)

        admin_role, created = Role.objects.get_or_create(name="admin")

        all_permissions = Permission.get_all()
        admin_role.permissions.set(all_permissions)
        admin_role.save()

        if created:
            if verbosity >= 1:
                self.stdout.write(self.style.SUCCESS("Created role: admin."))
        else:
            if verbosity >= 1:
                self.stdout.write(
                    "Admin role already exists. Permissions were updated."
                )
