# pyright: reportArgumentType=false
# pyright: reportAssignmentType=false
# pyright: reportIncompatibleVariableOverride=false
from django.db import models
from django.conf import settings

# Create your models here.
class CreatedByModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    class Meta:
        abstract = True

class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
        ordering = ['-modified', '-created']

class ActivatorModel(models.Model):
    class StatusChoice(models.IntegerChoices):
        INACTIVE = 0, 'Inactive'
        ACTIVE = 1, 'Active'

        
    status = models.IntegerField(
        choices=StatusChoice.choices,
        default=StatusChoice.ACTIVE.value,
    )

    class Meta:
        abstract = True
        ordering = ["status"]
class TitleModel(models.Model):
    title = models.CharField(max_length=255)
    class Meta:
        abstract = True
class DescriptionModel(models.Model):
    description = models.TextField(blank=True, null=True)
    class Meta:
        abstract = True

class TitleDescriptionModel(TitleModel, DescriptionModel):
    class Meta:
        abstract = True

class Client(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True)
    first_name = models.CharField()
    last_name = models.CharField()

