from django.db import models
from django.conf import settings

from core.models import ActivatorModel, TimeStampedModel

# Create your models here.
# pyright: reportIncompatibleVariableOverride=false
class Badge(TimeStampedModel, ActivatorModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    company_slug = models.SlugField()
    objects = models.Manager()

    class Meta:
        unique_together=('user', 'company_slug')
        abstract=True

class ClientBadge(Badge):
    pass
