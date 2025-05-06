from django.db import models


class PermissionGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

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
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def count_all(cls):
        return cls.objects.count()


class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    group = models.ForeignKey(
        PermissionGroup, on_delete=models.CASCADE, related_name="permissions"
    )

    def __str__(self):
        return self.name

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
    def exists_in_group(cls, group):
        return cls.objects.filter(group=group).exists()

    @classmethod
    def exists_in_groups(cls, groups):
        return cls.objects.filter(group__in=groups).exists()

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
    def get_by_group(cls, group):
        return cls.objects.filter(group=group)

    @classmethod
    def get_by_groups(cls, groups):
        return cls.objects.filter(group__in=groups)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def count_all(cls):
        return cls.objects.count()
