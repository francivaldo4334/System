# pyright: reportIncompatibleVariableOverride=false
from django.db import models

from core.models import ActivatorModel, TimeStampedModel

# Create your models here.
class ScheduleAppConfig(TimeStampedModel, ActivatorModel):
    company_image = models.ImageField(
        null=True,
        black=True,
    )
    company_name = models.CharField(
        null=True,
        black=True,
    )
    background_image = models.ImageField(
        null=True,
        black=True,
    )
    resource_visible_to_self_scheduling = models.ManyToManyField(
        'uri.URIModel',
    )

    class ActiveScheduleAppConfigExists(Exception):
        pass

    def save(self, *, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.__class__.objects.filter(status=self.StatusChoice.ACTIVE.value).exists():
            raise self.ActiveScheduleAppConfigExists()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
