# Generated by Django 5.2 on 2025-04-27 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("permissions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "permissions",
                    models.ManyToManyField(
                        related_name="roles", to="permissions.permission"
                    ),
                ),
            ],
        ),
    ]
