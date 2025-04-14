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

    def get_permissions(self):
        return self.permissions.all()

    def has_permission(self, permission_name):
        return self.permissions.filter(name=permission_name).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)


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
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="roles")

    def __str__(self):
        return self.name

    def get_permissions(self):
        return self.permissions.all()

    def get_permissions_by_group(self, group_name):
        return self.permissions.filter(group__name=group_name)

    def get_grouped_permissions(self):
        grouped_permissions = []

        for permission in self.permissions.select_related("group"):
            group_name = permission.group.name

            group_entry = next(
                (
                    entry
                    for entry in grouped_permissions
                    if entry["group"] == group_name
                ),
                None,
            )
            if not group_entry:
                group_entry = {"group": group_name, "permissions": []}
                grouped_permissions.append(group_entry)

            group_entry["permissions"].append(
                {"name": permission.name, "description": permission.description}
            )

        return grouped_permissions

    def has_permission(self, permission_name):
        return self.permissions.filter(name=permission_name).exists()

    def get_users(self):
        return User.objects.filter(role=self)

    @classmethod
    def role_exists(cls, role_name):
        return cls.objects.filter(name=role_name).exists()

    @classmethod
    def role_exists_by_id(cls, role_id):
        return cls.objects.filter(id=role_id).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)


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

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name or self.email.split("@")[0]

    def get_permissions(self):
        if self.role:
            return self.role.get_permissions()
        return Permission.objects.none()

    def get_permissions_by_group(self, group_name):
        if self.role:
            return self.role.get_permissions_by_group(group_name)
        return Permission.objects.none()

    def get_grouped_permissions(self):
        if self.role:
            return self.role.get_grouped_permissions()
        return {}

    def has_permission(self, permission_name):
        if self.role:
            return self.role.has_permission(permission_name)
        return False

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)
