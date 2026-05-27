from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
class CustomUser(AbstractUser):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        unique=True,
    )
    is_email_checked = models.BooleanField(
        default=False # type: ignore
    )
