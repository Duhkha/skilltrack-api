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


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

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
