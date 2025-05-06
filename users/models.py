from django.db import models
from django.utils import timezone
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from core.utils import normalize_string
from roles.models import Role


class CustomUserManager(UserManager):
    def _create_user(
        self, name, email, password, is_manually_created=False, **extra_fields
    ):
        email = normalize_string(email)
        name = name.strip()
        user = self.model(
            name=name,
            email=email,
            is_manually_created=is_manually_created,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(
        self, name, email, password, is_manually_created=False, **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            name, email, password, is_manually_created, **extra_fields
        )

    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(name, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    is_manually_created = models.BooleanField(default=False)
    temp_plaintext_password = models.CharField(max_length=128, null=True, blank=True)

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

    @classmethod
    def exists_by_id(cls, id):
        return cls.objects.filter(id=id).exists()

    @classmethod
    def exists_in_ids(cls, ids):
        return cls.objects.filter(id__in=ids).exists()

    @classmethod
    def exists_by_email(cls, email):
        return cls.objects.filter(email__iexact=email).exists()

    @classmethod
    def exists_in_emails(cls, emails):
        return any(cls.exists_by_email(email) for email in emails)

    @classmethod
    def exists_by_role(cls, role):
        return cls.objects.filter(role=role).exists()

    @classmethod
    def exists_in_roles(cls, roles):
        return cls.objects.filter(role__in=roles).exists()

    @classmethod
    def superuser_exists_in_role(cls, role):
        return cls.objects.filter(role=role, is_superuser=True).exists()

    @classmethod
    def superuser_exists_in_roles(cls, roles):
        return cls.objects.filter(role__in=roles, is_superuser=True).exists()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id)

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.filter(email__iexact=email)

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
    def get_superusers(cls):
        return cls.objects.filter(is_superuser=True)

    @classmethod
    def get_superusers_by_role(cls, role):
        return cls.objects.filter(role=role, is_superuser=True)

    @classmethod
    def get_superusers_in_ids(cls, ids):
        return cls.objects.filter(id__in=ids, is_superuser=True)

    @classmethod
    def get_superusers_in_roles(cls, roles):
        return cls.objects.filter(role__in=roles, is_superuser=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def count_all(cls):
        return cls.objects.count()
