# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
# pyright: reportArgumentType=false
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from core.models import ActivatorModel, CreatedByModel, TimeStampedModel, TitleDescriptionModel, TitleModel
from dateutil.rrule import rrulestr
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from schedule.flows import AssignmentSlotStateCancelled, AssignmentSlotStateCompleted, AssignmentSlotStateCreated, FlowState, AssignmentSlotStateInProgress, AssignmentSlotStateMigrated, NotStateError

# Create your models here.
class Resource(TimeStampedModel, ActivatorModel):
    name = models.CharField()
    parent = models.ForeignKey('self',models.CASCADE,'children', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^\d+(\.\d+)*$')])
    is_selectable = models.BooleanField()

    content_type = models.ForeignKey(ContentType, models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()

class ResourceNotSelectable(Resource):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_selectable=False)
    objects = Manager()
    class Meta:
        proxy = True

class ResourceSelectable(Resource):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_selectable=True)
    objects = Manager()
    class Meta:
        proxy = True

class Service(TimeStampedModel, ActivatorModel, TitleDescriptionModel):
    required_resource = models.ManyToManyField(ResourceNotSelectable, through='ServiceResourceRelation')

class ServiceResourceRelation(models.Model):
    service = models.ForeignKey(Service, models.CASCADE)
    resource_type = models.ForeignKey(ResourceNotSelectable, models.CASCADE)
    quantity = models.PositiveIntegerField()
    
def validate_rrule(value):
    if not value:
        return
    try:
        rrulestr(value)
    except Exception as e:
        raise ValidationError("Invalid RRule.")

class Availability(TimeStampedModel, ActivatorModel):
    # RULE | UMA UNIDADE DE SLOT REPRESENTA 5 MINUTOS
    resource = models.ForeignKey(ResourceSelectable, models.CASCADE)
    rrule_params = models.CharField(validators=[validate_rrule])
    # os campos 'valid_' e '_slot' são usados para consultas no banco
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    start_slot = models.PositiveSmallIntegerField()
    finish_slot = models.PositiveSmallIntegerField()


class ResourceOccupation(models.Model):
    resource = models.ForeignKey(ResourceSelectable, models.CASCADE)
    date = models.DateField()
    bitmap = models.CharField(max_length=288, validators=[RegexValidator(r'^[0-1]+$'), MinLengthValidator(288)])

    class Meta:
        unique_together = ['resource', 'date']


class AssignmentSlot(TimeStampedModel, CreatedByModel): #TODO: precisa de um state

    class Status(models.TextChoices):
        CREATED = 'CR', 'CREATED'
        IN_PROGRESS = 'NP', "In Progress"
        COMPLETED = 'CP', 'Completed'
        MIGRATED = 'MG', 'Migrated'
        CANCELLED = 'CL', 'Cancelled'

    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.CREATED.value)

    service = models.ForeignKey(Service, models.CASCADE)
    resources = models.ManyToManyField(ResourceSelectable)
    date = models.DateField()
    start_slot = models.PositiveSmallIntegerField()
    finish_slot = models.PositiveSmallIntegerField()
    @property
    def state(self) -> FlowState:
        states = {
            self.Status.CREATED.value: AssignmentSlotStateCreated,
            self.Status.IN_PROGRESS.value: AssignmentSlotStateInProgress,
            self.Status.COMPLETED.value: AssignmentSlotStateCompleted,
            self.Status.MIGRATED.value: AssignmentSlotStateMigrated,
            self.Status.CANCELLED.value: AssignmentSlotStateCancelled,
        }
        state_class = states.get(str(self.status))
        if not state_class: raise NotStateError()
        return state_class(self)
