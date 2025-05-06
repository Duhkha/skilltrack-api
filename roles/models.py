from django.db import models
from permissions.models import Permission


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="roles")

    def __str__(self):
        return self.name

    def has_permission(self, name):
        return self.permissions.filter(name__iexact=name).exists()

    def has_permissions(self, names):
        query = models.Q()
        for name in set(names):
            query |= models.Q(name__iexact=name)

        matched_count = self.permissions.filter(query).count()

        return matched_count >= len(set(names))

    def get_permission(self, name):
        return self.permissions.filter(name__iexact=name)

    def get_permissions(self):
        return self.permissions.all()

    def get_permissions_by_group(self, group):
        return self.permissions.filter(group=group)

    def get_permissions_by_groups(self, groups):
        return self.permissions.filter(group__in=groups)

    def get_grouped_permissions(self):
        grouped_permissions = []

        for permission in self.permissions.select_related("group"):
            group = permission.group

            group_entry = next(
                (entry for entry in grouped_permissions if entry["name"] == group.name),
                None,
            )

            if not group_entry:
                group_entry = {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "permissions": [],
                }
                grouped_permissions.append(group_entry)

            group_entry["permissions"].append(
                {
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                }
            )

        return grouped_permissions

    @classmethod
    def exists_by_id(cls, id):
        return cls.objects.filter(id=id).exists()

    @classmethod
    def exists_in_ids(cls, ids):
        return cls.objects.filter(id__in=ids).exists()

    @classmethod
    def exists_by_name(cls, name):
        return cls.objects.filter(name__iexact=name).exists()

    @classmethod
    def exists_in_names(cls, names):
        query = models.Q()
        for name in names:
            query |= models.Q(name__iexact=name)

        return cls.objects.filter(query).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id)

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_by_name(cls, name):
        return cls.objects.filter(name__iexact=name)

    @classmethod
    def get_by_names(cls, names):
        query = models.Q()
        for name in names:
            query |= models.Q(name__iexact=name)

        return cls.objects.filter(query)

    @classmethod
    def get_roles_with_all_permissions(cls):
        all_permissions_count = Permission.count_all()

        roles_with_all_permissions = Role.objects.annotate(
            permission_count=models.Count("permissions")
        ).filter(permission_count=all_permissions_count)

        return roles_with_all_permissions

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def count_all(cls):
        return cls.objects.count()
