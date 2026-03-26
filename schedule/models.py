# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
# pyright: reportArgumentType=false
# pyright: reportCallIssue=false
# pyright: reportGeneralTypeIssues=false
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models, transaction
from django.db.models.functions import Concat, Substr
from core.models import ActivatorModel, CreatedByModel, TimeStampedModel, TitleDescriptionModel
from dateutil.rrule import rrulestr, rruleset
from django.utils.translation import gettext_lazy as _
from schedule.flows import AssignmentStateCancelled, AssignmentStateCompleted, AssignmentStateConfirmed, AssignmentStatePeding, AssignmentState, AssignmentStateInProgress, AssignmentStateMigrated, NotStateError

# Create your models here.
class Resource(TimeStampedModel, ActivatorModel):
    name = models.CharField()
    parent = models.ForeignKey('ResourceNotSelectable',models.CASCADE,'children', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^([a-z0-9]+\.)*[a-z0-9]+\.?$')])
    is_selectable = models.BooleanField()
    uri = models.ForeignKey('uri.URIModel', models.CASCADE, blank=True, null=True)
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
    # 288 é a queantidade de slots de 5 minutos em um dia / 24 horas
    bitmap = models.CharField(max_length=288,
                              validators=[RegexValidator(r'^[0-1]+\Z'), MinLengthValidator(288)],
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
            with transaction.atomic():
                qs = self.all() 
                qs.update(
                    bitmap=Concat(
                        Substr('bitmap',1,start_slot),
                        models.Value('0' * duration_slot),
                        Substr('bitmap',start_slot + duration_slot + 1),
                        output_field=models.CharField()
                    )
                )
            return qs.filter(bitmap='0' * 288).delete()

    objects = QuerySet.as_manager()

    class Meta:
        unique_together = ['resource', 'date']

class Assignment(TimeStampedModel, CreatedByModel):
    class Status(models.TextChoices):
        PENDING = 'PD', _('Pending')
        CONFIRMED = 'CF', _('Confirmed')
        MIGRATED = 'MG', _('Migrated')
        CANCELLED = 'CC', _('Cancelled')
        ABSENT = 'AB', _('Absent')
        IN_PROGRESS = 'IP', _('In Progress')
        COMPLETED = 'CP', _('Completed')

    service = models.ForeignKey(Service, models.CASCADE, null=True, blank=True)
    resources = models.ManyToManyField(ResourceSelectable)
    date = models.DateField()
    start_slot = models.PositiveSmallIntegerField()
    duration_slot = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.PENDING.value)


    @property
    def state(self) -> AssignmentState:
        states = {
            self.Status.PENDING.value: AssignmentStatePeding,
            self.Status.CONFIRMED.value: AssignmentStateConfirmed,
            self.Status.IN_PROGRESS.value: AssignmentStateInProgress,
            self.Status.COMPLETED.value: AssignmentStateCompleted,
            self.Status.MIGRATED.value: AssignmentStateMigrated,
            self.Status.CANCELLED.value: AssignmentStateCancelled,
        }
        state_class = states.get(str(self.status))
        if not state_class: raise NotStateError()
        return state_class(self)
