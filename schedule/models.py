# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
from django.db import models
from core.models import ActivatorModel, CreatedByModel, TimeStampedModel, TitleDescriptionModel, TitleModel
from dateutil.rrule import rrulestr
from schedule.flows import FlowStateCancelled, FlowStateCompleted, FlowStateCreated, FlowState, FlowStateInProgress, FlowStateMigrated, NotStateError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
def is_valid_rrule(value):
    try:
        rrulestr(value)
        return True,
    except Exception:
        return False

class Resource(TimeStampedModel, ActivatorModel, TitleModel):
    content_type = models.ForeignKey(ContentType, models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

class Service(TimeStampedModel, ActivatorModel, TitleDescriptionModel):
    resoures = models.ManyToManyField(Resource, through='ServiceRequirementRelation')

class ServiceRequirementRelation(models.Model):
    service = models.ForeignKey(Service, models.CASCADE)
    resource = models.ForeignKey(Resource, models.CASCADE)
    quantity = models.PositiveIntegerField()
    
# RULE | UMA UNIDADE DE SLOT REPRESENTA 5 MINUTOS

class Availability(TimeStampedModel, ActivatorModel):
    resource = models.ForeignKey(Resource, models.CASCADE)
    rrule_params = models.CharField(validators=[is_valid_rrule])
    # os campos 'valid_' e '_slot' são usados para consultas no banco
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    start_slot = models.PositiveSmallIntegerField()
    finish_slot = models.PositiveSmallIntegerField()


class AssignmentSlot(TimeStampedModel, CreatedByModel): #TODO: precisa de um state
    resources = models.ManyToManyField(Resource)
    date = models.DateField()
    start_slot = models.PositiveSmallIntegerField()
    finish_slot = models.PositiveSmallIntegerField()

# class FlowStateModel(models.Model):
#     class Status(models.TextChoices):
#         OPEN = 'ON', 'Open'
#         IN_PROGRESS = 'NP', "In Progress"
#         COMPLETED = 'CP', 'Completed'
#         MIGRATED = 'MG', 'Migrated'
#         CANCELLED = 'CL', 'Cancelled'
#     status = models.CharField(max_lenght=2,
#                               choices=Status.choices,
#                               default=Status.OPEN.value)
#     class Meta:
#         abstract = True

#     @property
#     def state(self) -> FlowState:
#         states = {
#             self.Status.OPEN.value: FlowStateCreated,
#             self.Status.IN_PROGRESS.value: FlowStateInProgress,
#             self.Status.COMPLETED.value: FlowStateCompleted,
#             self.Status.MIGRATED.value: FlowStateMigrated,
#             self.Status.CANCELLED.value: FlowStateCancelled,
#         }
#         state_class = states.get(str(self.status))
#         if not state_class: raise NotStateError()
#         return state_class(self)

# class Appointment(Slot):
#     client = models.ForeignKey('core.Client', models.CASCADE)

# class Event(Slot, FlowStateModel, TitleDescriptionModel):
#     pass

# class TaskGroup(Slot, TitleDescriptionModel):
#     pass

# class Task(TitleModel):
#     task_group = models.ForeignKey(TaskGroup, models.CASCADE)
#     checked = models.BooleanField()
    


# class Appointment(
#     TimeStampedModel,
#     CreatedByModel,
# ):
