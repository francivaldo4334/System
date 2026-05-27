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
    is_active = models.BooleanField(
        _("active"),
        default=False, # type: ignore
        help_text=_( # type: ignore
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
