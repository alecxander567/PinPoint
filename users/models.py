import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), name=name)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    messenger_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    objects = UserManager()

    def __str__(self):
        return self.email


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.created_at + timedelta(hours=1)

    def __str__(self):
        return f"Token for {self.user.email} - Used: {self.used}"


class BugReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
