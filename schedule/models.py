# pyright: reportIncompatibleVariableOverride=false
from django.db import models
from core.models import ActivatorModel, CreatedByModel, TimeStampedModel
from django.conf import settings
from dateutil.rrule import rrulestr

# Create your models here.
def is_valid_rrule(value):
    try:
        rrulestr(value)
        return True,
    except Exception:
        return False

class Schedule(TimeStampedModel, ActivatorModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    rrule_params = models.CharField(validators=[is_valid_rrule])
    duration = models.DurationField()
    init = models.DateTimeField()
    end = models.DateTimeField()


class Appointment(
    TimeStampedModel,
    ActivatorModel,
    CreatedByModel,
):
    schedule = models.ForeignKey(Schedule, models.CASCADE)
    init = models.DateTimeField()
    end = models.DateTimeField()
