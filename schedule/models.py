# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportArgumentType=false
# pyright: reportCallIssue=false
# pyright: reportGeneralTypeIssues=false
from typing import List, cast
from django.contrib.auth.mixins import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models, transaction
from django.db.models.functions import Concat, Substr
from rest_framework.fields import MinValueValidator
from core.models import ActivatorModel, CreatedByModel, DescriptionModel, TimeStampedModel, TitleDescriptionModel
from dateutil.rrule import rrulestr
from django.utils.translation import gettext_lazy as _
from schedule.flows import AssignmentStateAbsent, AssignmentStateCancelled, AssignmentStateCompleted, AssignmentStateConfirmed, AssignmentStatePeding, AssignmentState, AssignmentStateInProgress, AssignmentStateMigrated, NotStateError
from datetime import datetime, time, timedelta
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Resource(TimeStampedModel, ActivatorModel):
    name = models.CharField()
    parent = models.ForeignKey('ResourceNotSelectable',models.PROTECT,'childrens', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^([a-z0-9]+\.)*[a-z0-9]+\.?$')])
    is_selectable = models.BooleanField()
    object_id = models.PositiveBigIntegerField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, models.CASCADE, blank=True, null=True)
    content_object = GenericForeignKey()
    class Meta:
        unique_together = ['content_type', 'object_id']
        ordering = ('parent_id','code')
        indexes = [
            models.Index(fields=['content_type', 'object_id'])
        ]
    def clean(self):
        if self.parent and not str(self.code).startswith(getattr(self.parent,'code')):
            raise ValidationError({'code': _('Enter a valid value.')})
        if not self.is_selectable and not str(self.code).endswith('.'):
            raise ValidationError({'code': _('Enter a valid value.')})
        if self.is_selectable and str(self.code).endswith('.'):
            raise ValidationError({'code': _('Enter a valid value.')})
    def save(self, *args, **kwargs):
        if self._state.adding and not self.code:
            self.code = self.get_next_code();
        if self.parent and self.parent.content_type:
            self.content_type = self.parent.content_type
            if not self.object_id:
                raise ValidationError({'object_id': _("Enter a valid value.")})
        return super().save(*args, **kwargs)

    def get_next_code(self):
        last = self.__class__.objects.order_by('-id').first()
        last_id = last.id if last else 0

        if self.is_selectable:
            if not self.parent:
                raise ValidationError({'parent': _('Enter a valid value.')})
            return f'{self.parent.code}.{last_id + 1}'

        return last_id + 1;

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

class ResourcePerson(Resource):
    class Manager(models.Manager):
        def get_queryset(self):
            from django.apps import apps
            from django.conf import settings
            user_model = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
            content_type = ContentType.objects.get_for_model(user_model)
    
            return super().get_queryset().filter(content_type=content_type)
    objects = Manager()
    class Meta:
        proxy = True

class ResourceObject(Resource):
    class Manager(models.Manager):
        def get_queryset(self):
            from django.apps import apps
            from django.conf import settings
            user_model = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
            content_type = ContentType.objects.get_for_model(user_model)
    
            return super().get_queryset().exclude(content_type=content_type)
    objects = Manager()
    class Meta:
        proxy = True

class Service(TimeStampedModel, ActivatorModel, TitleDescriptionModel):
    required_resources = models.ManyToManyField(ResourceNotSelectable, through='ServiceResourceRelation')

class ServiceResourceRelation(models.Model):
    service = models.ForeignKey(Service, models.CASCADE)
    resource_type = models.ForeignKey(ResourceNotSelectable, models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        unique_together = ('service', 'resource_type')


class Availability(TimeStampedModel, ActivatorModel, DescriptionModel):
    class ConflitError(ValidationError):
        def __init__(self):
            super().__init__(_('There is a schedule conflict for the selected date and time range.'))

    class MaxValidError(ValidationError):
        def __init__(self):
            super().__init__(_('There cannot be an availability period greater than 90 days.'))

    class QuerySet(models.QuerySet):
        def filter_date_colision(self, start: datetime.date, end:datetime.date):
            return self.filter(
                valid_until__gte=start,
                valid_from__lte=end,
            )
        def filter_time_colision(self, start:datetime.time, end: datetime.time):
            return self.filter(
                time_from__lte=end,
                time_until__gte=start,
            )
    objects = QuerySet.as_manager()
    # RULE | UMA UNIDADE DE SLOT REPRESENTA 5 MINUTOS
    rrule_params = models.CharField(validators=[
        RegexValidator(r"^DTSTART:{%DATE%}T\d{6}\nRRULE:FREQ=MINUTELY;UNTIL={%DATE%}T\d{6}Z?;INTERVAL=\d+;BYDAY=[A-Z]{2}(?:,[A-Z]{2})*Z"),
    ])
    valid_from = models.DateField()
    valid_until = models.DateField()
    time_from = models.TimeField()
    time_until = models.TimeField()
    duration_slot = models.PositiveSmallIntegerField()
    interval_slot = models.PositiveSmallIntegerField()

    def get_occurrences(self, init: datetime.date, end: datetime.date) -> List[datetime]:
        if init < self.valid_from:
            init = self.valid_from
        if self.valid_until and end > self.valid_until:
            end = self.valid_until;
        results = []
        search_start = datetime.combine(init, time.min)
        search_end = datetime.combine(end, time.max)
    
        current_date:datetime = search_start
        while current_date <= search_end :
            rrule = rrulestr(str(self.rrule_params).replace("{%DATE%}", current_date.strftime("%Y%m%d")))
            occurrences = rrule.between(search_start, search_end, True)
            results.extend(occurrences)
            current_date += timedelta(days=1)
        return sorted(list(set(results)))
    def get_map(self, date: datetime.date):
        occurrences:List[datetime]  = self.get_occurrences(date, date)
        map = [0] * 288
        for occ in occurrences:
            start_slot = ((occ.hour * 60) + occ.minute) // 5
            map[start_slot] = 1
            for occuped_slot in range(self.duration_slot):
                map[start_slot + occuped_slot] = 1
        return map

    def save(self, *args, **kwargs):
        if self.valid_until > self.valid_from + timedelta(days=90): # type: ignore
            raise Availability.MaxValidError()
        
        if avs_with_conflit := list(self.__class__.objects.filter_date_colision(
            self.valid_from,
            self.valid_until or datetime.max
        ).filter_time_colision(
            self.time_from,
            self.time_until,
        ).exclude(pk=self.pk)):
            date = datetime.combine(self.valid_from, time.min)
            end = datetime.combine(self.valid_until, time.max)
            while date <= end:
                curr_map = self.get_map(date.date())
                curr_indexes = [i for i, v in enumerate(curr_map) if v == 1]
                for _av in avs_with_conflit:
                    av = cast('Availability', _av)
                    other_map = av.get_map(date.date())
                    other_indexes = [i for i, v in enumerate(other_map) if v == 1]
                    if any(n in curr_indexes  for n in other_indexes):
                        raise Availability.ConflitError()
                date += timedelta(days=1)
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
    class QuerySet(models.QuerySet):
        def visibles(self):
            return self.exclude(
                status__in=[
                   Assignment.Status.CANCELLED.value,
                   Assignment.Status.ABSENT.value,
                ]
            )
    objects = QuerySet.as_manager()
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
            self.Status.ABSENT.value: AssignmentStateAbsent,
        }
        state_class = states.get(str(self.status))
        if not state_class: raise NotStateError()
        return state_class(self)
