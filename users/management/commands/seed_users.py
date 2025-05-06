from django.core.management.base import BaseCommand
from roles.models import Role
from users.models import User


class Command(BaseCommand):
    help = "Seed admin user."

    def handle(self, *args, **kwargs):
        verbosity = kwargs.get("verbosity", 1)

        admin_email = "admin@example.com"
        if not User.objects.filter(email=admin_email).exists():
            admin_role = Role.objects.get(name="admin")

            User.objects.create_user(
                name="Admin",
                email=admin_email,
                password="Admin123!",
                role=admin_role,
                is_staff=True,
                is_superuser=True,
            )

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(f"Created admin user: {admin_email}.")
                )
        else:
            if verbosity >= 1:
                self.stdout.write(f"Admin user already exists: {admin_email}.")
