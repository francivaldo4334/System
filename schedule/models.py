# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
# pyright: reportArgumentType=false
# pyright: reportCallIssue=false
# pyright: reportGeneralTypeIssues=false
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models.functions import Concat, Substr
from core.models import ActivatorModel, CreatedByModel, TimeStampedModel, TitleDescriptionModel, TitleModel
from dateutil.rrule import rrulestr, rruleset
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from schedule.flows import AssignmentSlotStateCancelled, AssignmentSlotStateCompleted, AssignmentSlotStateConfirmed, AssignmentSlotStateCreated, AssignmentSlotState, AssignmentSlotStateInProgress, AssignmentSlotStateMigrated, NotStateError

# Create your models here.
class Resource(TimeStampedModel, ActivatorModel):
    name = models.CharField()
    parent = models.ForeignKey('ResourceNotSelectable',models.CASCADE,'children', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^([a-z0-9]+\.)*[a-z0-9]+\.?$')])
    is_selectable = models.BooleanField()

    content_type = models.ForeignKey(ContentType, models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()

    def clean(self):
        if self.parent and not str(self.code).startswith(getattr(self.parent,'code')):
            raise ValidationError({'code': _('Enter a valid value.')})
        if not self.is_selectable and not str(self.code).endswith('.'):
            raise ValidationError({'code': _('Enter a valid value.')})
        if self.is_selectable and str(self.code).endswith('.'):
            raise ValidationError({'code': _('Enter a valid value.')})

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
    required_resources = models.ManyToManyField(ResourceNotSelectable, through='ServiceResourceRelation')

class ServiceResourceRelation(models.Model):
    service = models.ForeignKey(Service, models.CASCADE)
    resource_type = models.ForeignKey(ResourceNotSelectable, models.CASCADE)
    quantity = models.PositiveIntegerField()


    
def rrule_validator(value):
    if not value:
        return
    if "DTSTART" not in value.upper():
        raise ValidationError(_("Enter a valid value."))
    if "UNTIL" not in value.upper():
        raise ValidationError(_("Enter a valid value."))
    try:
        rrulestr(value)
    except Exception as e:
        raise ValidationError(_("Enter a valid value."))

class Availability(TimeStampedModel, ActivatorModel):
    # RULE | UMA UNIDADE DE SLOT REPRESENTA 5 MINUTOS
    resource = models.ForeignKey(ResourceSelectable, models.CASCADE)
    rrule_params = models.CharField(validators=[rrule_validator])
    valid_from = models.DateField(editable=False)
    valid_until = models.DateField(editable=False)
    start_slot = models.PositiveSmallIntegerField(editable=False)
    duration_slot = models.PositiveSmallIntegerField()

    def save(self, *args, **kwargs):
        rule:rruleset = rrulestr(self.rrule_params)
        dtstart = getattr(rule,'_dtstart')
        until = getattr(rule, '_until')

        self.valid_from = dtstart.date()
        self.valid_until = until.date()
        self.start_slot = (dtstart.hour * 60 + dtstart.minute) // 5
        return super().save(*args, **kwargs)


class ResourceOccupation(models.Model):
    resource = models.ForeignKey(ResourceSelectable, models.CASCADE)
    date = models.DateField()
    bitmap = models.CharField(max_length=288,
                              validators=[RegexValidator(r'^[0-1]+$'), MinLengthValidator(288)],
                              default='0'*288)
    class QuerySet(models.QuerySet):
        def available(self,start_slot, duration_slot):
            return self.filter(
                bitmap__regex=f'^.{{{start_slot}}}0{{{duration_slot}}}'
            )
        def occupy(self, start_slot, duration_slot):
            return self.update(
                bitmap=Concat(
                    Substr('bitmap',1,start_slot),
                    models.Value('1' * duration_slot),
                    Substr('bitmap',start_slot + duration_slot + 1),
                    output_field=models.CharField()
                )
            )
        def vacate(self, start_slot, duration_slot):
            return self.update(
                bitmap=Concat(
                    Substr('bitmap',1,start_slot),
                    models.Value('0' * duration_slot),
                    Substr('bitmap',start_slot + duration_slot + 1),
                    output_field=models.CharField()
                )
            )
    objects = QuerySet.as_manager()

    class Meta:
        unique_together = ['resource', 'date']


class AssignmentSlot(TimeStampedModel, CreatedByModel):
    class Status(models.TextChoices):
        CREATED = 'CR', _('Created')
        CONFIRMED = 'CF', _('Confirmed')
        IN_PROGRESS = 'NP', _('In Progress')
        COMPLETED = 'CP', _('Completed')
        MIGRATED = 'MG', _('Migrated')
        CANCELLED = 'CL', _('Cancelled')

    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.CREATED.value)

    service = models.ForeignKey(Service, models.CASCADE, null=True, blank=True)
    resources = models.ManyToManyField(ResourceSelectable)
    date = models.DateField()
    start_slot = models.PositiveSmallIntegerField()
    duration_slot = models.PositiveSmallIntegerField()

    @property
    def state(self) -> AssignmentSlotState:
        states = {
            self.Status.CREATED.value: AssignmentSlotStateCreated,
            self.Status.CONFIRMED.value: AssignmentSlotStateConfirmed,
            self.Status.IN_PROGRESS.value: AssignmentSlotStateInProgress,
            self.Status.COMPLETED.value: AssignmentSlotStateCompleted,
            self.Status.MIGRATED.value: AssignmentSlotStateMigrated,
            self.Status.CANCELLED.value: AssignmentSlotStateCancelled,
        }
        state_class = states.get(str(self.status))
        if not state_class: raise NotStateError()
        return state_class(self)
