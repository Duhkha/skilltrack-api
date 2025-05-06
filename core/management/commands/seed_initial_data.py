from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Seed all initial data."

    def handle(self, *args, **kwargs):
        verbosity = kwargs.get("verbosity", 1)

        call_command("seed_permissions", verbosity=verbosity)
        call_command("seed_roles", verbosity=verbosity)
        call_command("seed_users", verbosity=verbosity)

        self.stdout.write(self.style.SUCCESS("✅ Seeding completed successfully."))
