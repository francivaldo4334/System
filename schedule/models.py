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

class Availability(TimeStampedModel, ActivatorModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    rrule_params = models.CharField(validators=[is_valid_rrule])
    duration = models.DurationField()
    start_at = models.DateTimeField()
    finish_at = models.DateTimeField()


class Appointment(
    TimeStampedModel,
    CreatedByModel,
):
    availability = models.ForeignKey(Availability, models.CASCADE)
    start_at = models.DateTimeField()
    duration = models.DurationField()
