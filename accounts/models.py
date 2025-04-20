from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(UserManager):
    def _create_user(self, name, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(name, email, password, **extra_fields)

    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(name, email, password, **extra_fields)


class PermissionGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def has_permission(self, name):
        return self.permissions.filter(name=name).exists()

    def has_permissions(self, names):
        return all(self.has_permission(name) for name in names)

    def get_permission(self, name):
        return self.permissions.filter(name=name).first()

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
        return cls.objects.filter(name=name).exists()

    @classmethod
    def exists_in_names(cls, names):
        return cls.objects.filter(name__in=names).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_by_name(cls, name):
        return cls.objects.filter(name=name).first()

    @classmethod
    def get_by_names(cls, names):
        return cls.objects.filter(name__in=names)

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

    def get_group_name(self):
        return self.group.name

    @classmethod
    def exists_by_id(cls, id):
        return cls.objects.filter(id=id).exists()

    @classmethod
    def exists_in_ids(cls, ids):
        return cls.objects.filter(id__in=ids).exists()

    @classmethod
    def exists_by_name(cls, name):
        return cls.objects.filter(name=name).exists()

    @classmethod
    def exists_in_names(cls, names):
        return cls.objects.filter(name__in=names).exists()

    @classmethod
    def exists_in_group(cls, group):
        return cls.objects.filter(group=group).exists()

    @classmethod
    def exists_in_groups(cls, groups):
        return cls.objects.filter(group__in=groups).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_by_name(cls, name):
        return cls.objects.filter(name=name).first()

    @classmethod
    def get_by_names(cls, names):
        return cls.objects.filter(name__in=names)

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


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="roles")

    def __str__(self):
        return self.name

    def has_permission(self, name):
        return self.permissions.filter(name=name).exists()

    def has_permissions(self, names):
        return all(self.has_permission(name) for name in names)

    def get_permission(self, name):
        return self.permissions.filter(name=name).first()

    def get_permissions(self):
        return self.permissions.all()

    def get_permissions_by_group(self, name):
        return self.permissions.filter(group=name)

    def get_permissions_by_groups(self, names):
        return self.permissions.filter(group__in=names)

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

    def get_users(self):
        return User.objects.filter(role=self)

    @classmethod
    def exists_by_id(cls, id):
        return cls.objects.filter(id=id).exists()

    @classmethod
    def exists_in_ids(cls, ids):
        return cls.objects.filter(id__in=ids).exists()

    @classmethod
    def exists_by_name(cls, name):
        return cls.objects.filter(name=name).exists()

    @classmethod
    def exists_in_names(cls, names):
        return cls.objects.filter(name__in=names).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_by_name(cls, name):
        return cls.objects.filter(name=name).first()

    @classmethod
    def get_by_names(cls, names):
        return cls.objects.filter(name__in=names)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def count_all(cls):
        return cls.objects.count()


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.name} ({self.email})"

    def has_permission(self, name):
        if self.role:
            return self.role.has_permission(name)

        return False

    def has_permissions(self, names):
        if self.role:
            return self.role.has_permissions(names)

        return False

    def get_permission(self, name):
        if self.role:
            return self.role.get_permission(name)

        return None

    def get_permissions(self):
        if self.role:
            return self.role.get_permissions()

        return Permission.objects.none()

    def get_permissions_by_group(self, name):
        if self.role:
            return self.role.get_permissions_by_group(name)

        return Permission.objects.none()

    def get_grouped_permissions(self):
        if self.role:
            return self.role.get_grouped_permissions()

        return []

    @classmethod
    def exists_by_id(cls, id):
        return cls.objects.filter(id=id).exists()

    @classmethod
    def exists_in_ids(cls, ids):
        return cls.objects.filter(id__in=ids).exists()

    @classmethod
    def exists_by_email(cls, email):
        return cls.objects.filter(email=email).exists()

    @classmethod
    def exists_in_emails(cls, emails):
        return cls.objects.filter(email__in=emails).exists()

    @classmethod
    def exists_by_role(cls, role):
        return cls.objects.filter(role=role).exists()

    @classmethod
    def exists_in_roles(cls, roles):
        return cls.objects.filter(role__in=roles).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.filter(email=email).first()

    @classmethod
    def get_by_emails(cls, emails):
        return cls.objects.filter(email__in=emails)

    @classmethod
    def get_by_role(cls, role):
        return cls.objects.filter(role=role)

    @classmethod
    def get_by_roles(cls, roles):
        return cls.objects.filter(role__in=roles)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def count_all(cls):
        return cls.objects.count()
