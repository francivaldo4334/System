# pyright: reportIncompatibleVariableOverride=false
from django.core.validators import RegexValidator
from django.db import models

from core.models import ActivatorModel, TimeStampedModel

# Create your models here.
class AppConfig(TimeStampedModel, ActivatorModel):
    company_image = models.ImageField(
        null=True,
        blank=True,
    )
    company_name = models.CharField(
        null=True,
        blank=True,
    )
    background_image = models.ImageField(
        null=True,
        blank=True,
    )
    class ActiveScheduleAppConfigExists(Exception):
        pass

    def save(self, *, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.__class__.objects.filter(status=self.StatusChoice.ACTIVE.value).exclude(pk=self.pk).exists(): # type: ignore
            raise self.ActiveScheduleAppConfigExists()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta:
        ordering = ('status', 'created')

class ResourceSlugVisible(models.Model):
    resource_slug = models.SlugField()
    subtitle = models.CharField()
    config = models.ForeignKey(AppConfig, models.CASCADE, 'resources_visibles')

    class Meta:
        unique_together = ('config', 'resource_slug')
