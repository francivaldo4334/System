# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
from django.db import models
from core.models import ActivatorModel, CreatedByModel, TimeStampedModel
from django.conf import settings
from dateutil.rrule import rrulestr
from schedule.flows import FlowStateCancelled, FlowStateCompleted, FlowStateCreated, FlowState, FlowStateInProgress, FlowStateMigrated, NotStateError

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


class Slot(TimeStampedModel, CreatedByModel):
    availability = models.ForeignKey(Availability, models.CASCADE)
    start_at = models.DateTimeField()
    duration = models.DurationField()
    class Meta:
        abstract = True

class FlowStateModel(models.Model):
    class Status(models.TextChoices):
        OPEN = 'ON', 'Open'
        IN_PROGRESS = 'NP', "In Progress"
        COMPLETED = 'CP', 'Completed'
        MIGRATED = 'MG', 'Migrated'
        CANCELLED = 'CL', 'Cancelled'
    status = models.CharField(max_lenght=2,
                              choices=Status.choices,
                              default=Status.OPEN.value)
    class Meta:
        abstract = True

    @property
    def state(self) -> FlowState:
        states = {
            self.Status.OPEN.value: FlowStateCreated,
            self.Status.IN_PROGRESS.value: FlowStateInProgress,
            self.Status.COMPLETED.value: FlowStateCompleted,
            self.Status.MIGRATED.value: FlowStateMigrated,
            self.Status.CANCELLED.value: FlowStateCancelled,
        }
        state_class = states.get(str(self.status))
        if not state_class: raise NotStateError()
        return state_class(self)

class Appointment(Slot):
    client = models.ForeignKey('core.Client', models.CASCADE)

class Event(Slot):
    ...

class Task(FlowStateModel):
    pass

class TaskGroup(Slot):
    ...
    


# class Appointment(
#     TimeStampedModel,
#     CreatedByModel,
# ):
