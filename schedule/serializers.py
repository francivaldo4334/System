from datetime import timedelta
from typing import Any
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from authentication.services import SendEmail
from schedule.models import Assignment, Availability, Resource, ResourceNotSelectable, ResourceObject, ResourceOccupation, ResourceSelectable, Service, ServiceResourceRelation, TimeBlock
from django.utils.translation import gettext_lazy as _

from schedule.services import LinkGenerator
from schedule.utils import ReourceQuantityNotEguals, ResourceNotAllowed, ResourceOcuppied, ServiceIsRequired, slot_to_time, time_to_slots


class ResourceCategorySerializer(serializers.ModelSerializer):
    resource_type = serializers.ChoiceField(
        choices=[
            ("PERSON", "Pessoa"),
            ("OBJECT", "Objeto"),
        ],
        write_only=True
    )
    resource_type_label = serializers.SerializerMethodField()
    class Meta:
        model = ResourceNotSelectable
        fields = [
            "id",
            "name",
            "choice_type",
            "resource_type",
            'resource_type_label',
        ]

    def get_resource_type_label(self, obj):
        content_type = self.context.get("user_content_type")
        return _("System user") if obj.content_type == content_type else _("Object")

    def save(self, **kwargs):
        if not self.validated_data: raise
        resource_type = self.validated_data.pop("resource_type")

        if resource_type == "PERSON":
            content_type = self.context.get("user_content_type")
            kwargs['content_type'] = content_type
        if resource_type == "OBJECT":
            kwargs['content_type'] = None
        kwargs['is_selectable'] = False
        return super().save(**kwargs)
class ResourceSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    parent_label = serializers.CharField(source='parent.name',
                                         allow_null=True,
                                         read_only=True)
    class Meta:
        model = Resource
        fields = [
            'id',
            'name',
            'code',
            'object_id',
            'label',
            'parent_label',
        ]
        read_only_fields = [
            'code',
        ]
    def get_label(self, obj: Resource):
        name = _(obj.name)
        if obj.parent:
            prefix = self.get_label(obj.parent) # type:ignore
            return  f'{prefix} / {name}'
        return name


    def create(self, validated_data):
        validated_data['is_selectable'] = True
        parent_code = self.context.get('parent_code')
        validated_data['parent'] = get_object_or_404(ResourceNotSelectable, code=parent_code)
        return super().create(validated_data)

class ResourceObjectSerializer(ResourceSerializer):
    class Meta:
        model = ResourceObject
        fields = [
            'id',
            'label',
            'name',
            'code',
            'parent_label',
            'object_id',
        ]
        read_only_fields = [
            'code',
        ]
class ResourcePersonSerializer(ResourceSerializer):
    username = serializers.CharField(write_only=True)
    class Meta:
        model = ResourceObject
        fields = [
            'id',
            'label',
            'username',
            'code',
            'parent_label',
            'object_id',
        ]
        read_only_fields = [
            'code',
        ]
    def to_representation(self, instance):
        return {
            **super().to_representation(instance),
            'username':instance.content_object.username
        }
    def create(self, validated_data):
        username = validated_data.pop('username', None)
        validated_data['name'] = validated_data.get('name', '')
        if username:
            from django.apps import apps
            from django.conf import settings
            user_model = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
            user = get_object_or_404(user_model, username=username)
            validated_data['object_id'] = user.pk
            validated_data['name'] = user.get_full_name()
        return super().create(validated_data)
    def update(self, instance, validated_data):
        username = validated_data.pop('username', None)
        validated_data['name'] = validated_data.get('name', '')
        if username:
            from django.apps import apps
            from django.conf import settings
            user_model = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
            user = get_object_or_404(user_model, username=username)
            validated_data['object_id'] = user.pk
            validated_data['name'] = user.get_full_name()
        return super().update(instance, validated_data)

class ServiceResourceRelationSerializer(serializers.ModelSerializer):
    service_label = serializers.ReadOnlyField(source='service.title')
    resource_type_label = serializers.ReadOnlyField(source='resource_type.name')
    resource_type_name = serializers.ReadOnlyField(source="resource_type.name")
    class Meta:
        model = ServiceResourceRelation
        fields = [
            'id',
            'service',
            'resource_type',
            'quantity',
            'resource_type_name',
            'service_label',
            'resource_type_label',
        ]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ServiceResourceRelation.objects.all(),
                fields=['service', 'resource_type'],
                message=_('A rule already exists between this Service and this Resource.')
            )
        ]


class ServiceSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="title")
    required_resources_label = serializers.SerializerMethodField()
    service_resource_relation = ServiceResourceRelationSerializer(
        source="serviceresourcerelation_set",
        many=True,
        read_only=True,
    )
    required_resources = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=ResourceNotSelectable.objects.all()
    )
    class Meta:
        model = Service
        fields = [
            'id',
            'label',
            'price',
            'description',
            'required_resources',
            'required_resources_label',
            'service_resource_relation',
        ]

    def get_required_resources_label(self, obj):
        if not hasattr(obj, 'required_resources'):
            return None;
        resource_labels = obj.required_resources.values_list('name', flat=True)
        return ','.join(resource_labels)


class AssignmentSerializer(serializers.ModelSerializer):
    availability = serializers.PrimaryKeyRelatedField(
        queryset=Availability.objects.all(),
        write_only=True,
    )
    resources = serializers.PrimaryKeyRelatedField(
        queryset=ResourceSelectable.objects.all(), 
        many=True
    )
    service_name = serializers.ReadOnlyField(source="service.title")
    resource_names = serializers.SerializerMethodField()
    google_calendar_link = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id',
            'service',
            'resources',
            'date',
            'start_slot',
            'duration_slot',
            'availability',
            'service_name',
            'resource_names',
            'status',
            'google_calendar_link',
        ]
        read_only_fields = [
            'duration_slot',
        ]

    def get_google_calendar_link(self,obj):
        return LinkGenerator().get_google_calendar_link(obj)

    def get_resource_names(self, obj):
        return [f'{r.parent.name}/{r.name}' for r in obj.resources.all()]

    def create(self, validated_data):
        request = self.context.get('request')
        availability = validated_data.pop('availability')
        user_client_resource = validated_data.pop('user_client_resource', None)

        resources = validated_data.pop('resources', [])
        if user_client_resource and user_client_resource not in resources:
            resources.append(user_client_resource)

        validated_data['duration_slot'] = availability.duration_slot
        validated_data['created_by'] = getattr(request,'user')
        instance =  Assignment.objects.create(**validated_data)
        instance.resources.set([r.pk for r in resources]) 
        return instance;

# pyright: reportAttributeAccessIssue=false
class CreateAssigmentSerializer(AssignmentSerializer):
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )
    resources = serializers.PrimaryKeyRelatedField(
                queryset=Resource.objects.all(),
        many=True
    )
    default_error_messages = {
        'resourcenotallowed': _('One or more selected resources are not allowed for this service type.') + "{msg}",
        'reourcequantitynoteguals': _('The provided resource quantity does not match the requirement for this service.') + "{msg}",
        'resourceocuppied': _('One or more selected resources are already occupied at the requested time.') + "{msg}",
        'serviceisrequired': _('Service is required for creating this assignment.') + "{msg}",
    }
    @transaction.atomic()
    def create(self, validated_data):
        try:
            instance:Assignment = super().create(validated_data)
            instance.state.confirm()
            user_resource = instance.resources.all().filter(
                parent__code="client"
            ).first()
            user = user_resource.content_object
            SendEmail().send_email_ticket(
                instance,
                self.context.get('request'),
                user,
            )
            return instance
        except ReourceQuantityNotEguals as e:
            raise self.fail('reourcequantitynoteguals', msg=e.args)
        except ResourceNotAllowed as e:
            raise self.fail('resourcenotallowed', msg=e.args)
        except ResourceOcuppied as e:
            raise self.fail('resourceocuppied', msg=e.args)
        except ServiceIsRequired as e:
            raise self.fail('serviceisrequired', msg=e.args)
        

class AvailabilitySerializer(serializers.ModelSerializer):
    week = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[(i, str(i)) for i in range(7)],
        ),
        write_only=True,
        required=True
    )
    time_from = serializers.TimeField(required=True)
    time_until = serializers.TimeField(required=False)
    duration = serializers.TimeField(write_only=True, required=True)
    interval = serializers.TimeField(write_only=True, required=True)

    class Meta:
        model = Availability
        fields = [
            "id", "description", "valid_from", "valid_until",
            "week", "time_from", "time_until", "duration", "interval",
            "rrule_params", "duration_slot", "interval_slot"
        ]
        extra_kwargs = {
            'rrule_params': {'read_only': True},
            'duration_slot': {'read_only': True},
            'interval_slot': {'read_only': True},
        }

    def _get_slot_count(self, init:int, end:int, duration: int, interval:int):
        return (end - init + interval) // (duration + interval)
    def _get_slots(self,t):
        return (t.hour * 60 + t.minute) // 5

    def validate(self, attrs):
        from datetime import datetime
        from dateutil.rrule import rrule, MINUTELY
        import re


        week_days = attrs.get('week')
        time_from = attrs.get('time_from')
        time_until = attrs.get('time_until')
        valid_from = attrs.get('valid_from')
        valid_until = attrs.get('valid_until', None)
        duration_time = attrs.get('duration')
        interval_time = attrs.get('interval')

        slot_from = self._get_slots(time_from)
        slot_until = self._get_slots(time_until)
        slot_duration = self._get_slots(duration_time)
        slot_interval = self._get_slots(interval_time)

        rrule_count = self._get_slot_count(slot_from, slot_until, slot_duration, slot_interval)
        rrule_weekdays = list(set(week_days))
        rrule_dtstart = datetime.combine(valid_from, time_from)
        rrule_until = datetime.combine(valid_until, time_until) if valid_until else None
        rrule_interval = (slot_duration + slot_interval) * 5

        rrule_instance = rrule(
              dtstart=rrule_dtstart,
              until=rrule_until,
              count=rrule_count,
              byweekday=rrule_weekdays,
              interval=rrule_interval,
              freq=MINUTELY,
        )

        attrs['rrule_params'] = re.sub(r"(DTSTART:|UNTIL=)\d{8}T", r"\1{%DATE%}T", str(rrule_instance))
        attrs['duration_slot'] = slot_duration
        attrs['interval_slot'] = slot_interval

        for field in ['week', 'duration', 'interval']:
            attrs.pop(field, None)

        return attrs

    def to_representation(self, instance):
        from dateutil.rrule import rrulestr
        data = super().to_representation(instance)
    
        try:
            rrule_str = str(data.get("rrule_params", ""))
            formatted_date = instance.valid_from.strftime("%Y%m%d")
            rule = rrulestr(rrule_str.replace("{%DATE%}", formatted_date))
            if hasattr(rule, '_byweekday'):
                data["week"] = list(set(rule._byweekday))
            total_minutes_dur = instance.duration_slot * 5
            total_minutes_int = instance.interval_slot * 5        
            data["duration"] = f"{total_minutes_dur // 60:02d}:{total_minutes_dur % 60:02d}"
            data["interval"] = f"{total_minutes_int // 60:02d}:{total_minutes_int % 60:02d}"

        except Exception as e:
            data["_conversion_error"] = str(e)        
        return data
    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except Availability.MaxValidError:
            raise serializers.ValidationError({
                'valid_until': _('There cannot be an availability period greater than 90 days.')
            })
        except Availability.ConflitError:
            raise serializers.ValidationError({
                'non_field_erros':_("There is a schedule conflict for the selected date and time range."),
            })

class AvailabilityPresentationSerializer(serializers.ModelSerializer):
    occurrences = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = [
            "id",
            "valid_from",
            "valid_until",
            "occurrences",
            "duration_slot",
            "description",
        ]
    def _get_all_occurrences_by_availability(self, av: Availability):
        from datetime import datetime
        dt_after_str = self.context.get('dt_after')
        dt_before_str = self.context.get('dt_before')
        if not dt_before_str or not dt_after_str:
            return []
        dt_before = datetime.strptime(dt_before_str, '%Y-%m-%d').date()
        dt_after = datetime.strptime(dt_after_str, '%Y-%m-%d').date()
        current_time = self.context.get('current_time')
        tm_current_time = datetime.strptime(current_time, '%H:%M').time() if current_time else None
        occurrences = av.get_occurrences(dt_after, dt_before, tm_current_time)
        return occurrences

    def get_occurrences(self, obj: Availability):
        from collections import defaultdict
        from datetime import datetime
        occupation_qs: Any = self.context.get('occupation_qs')
        occurrences = self._get_all_occurrences_by_availability(obj)
        occurrences_map_slots = defaultdict(list)
        for occ in occurrences:
            occurrences_map_slots[occ.date()].append(occ.time())
        results = []
        for dt, times in occurrences_map_slots.items():
            for time in times:
                if occupation_qs.available(time_to_slots(time), obj.duration_slot).exists():
                    results.append(datetime.combine(dt, time))
        return results

        def map_bitmap_to_index(bit_string: str) -> list[int]:
            return [i for i, it in enumerate(bit_string) if it == '1']

        dt_after_str = self.context.get('dt_after')
        dt_before_str = self.context.get('dt_before')
    
        if not dt_before_str or not dt_after_str:
            return []

        # Parsing de datas
        # dt_before = datetime.strptime(dt_before_str, '%Y-%m-%d').date()
        # dt_after = datetime.strptime(dt_after_str, '%Y-%m-%d').date()

        current_time = self.context.get('current_time')
        # tm_current_time = datetime.strptime(current_time, '%H:%M').time() if current_time else None

        # 2. Pré-processar o mapa de ocupações (O(M))
        # Criamos um set() para cada data, pois a busca 'in' no set é O(1), muito mais rápida que em listas
        occupations = self.context.get('occupations', [])
        occupation_map = defaultdict(list)
        for occ in occupations:
            occupation_map[occ.date].extend(map_bitmap_to_index(occ.bitmap))

        results = []
        # occurrences = obj.get_occurrences(dt_after, dt_before, tm_current_time)
        # 3. Loop Único para Filtragem e Construção do Resultado
        for occ in occurrences:
            occ_date = occ.date()
            slot = time_to_slots(occ.time())
            # Se o slot não estiver ocupado naquela data, já adicionamos o datetime final à lista
            if slot not in occupation_map.get(occ_date, set()):
                results.append(datetime.combine(occ_date, slot_to_time(slot)))
        return results
class ActionMigrateSerializer(serializers.Serializer):
    availability = serializers.PrimaryKeyRelatedField(
        queryset=Availability.objects.all()
    )
    start_slot = serializers.IntegerField()
    date = serializers.DateField()
    duration_slot = serializers.ReadOnlyField()

    def save(self, **kwargs):
        data = self.validated_data
        availability = data.get('availability', None)
        duration_slot = availability.duration_slot if availability else None
        start_slot = data.get('start_slot', None)
        date = data.get('date', None)
        result = {
            'duration_slot': duration_slot,
            'start_slot': start_slot,
            'date': date,
        }
        return result


class DashboardSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Assignment.Status.choices)
    total = serializers.IntegerField()


class TimeBlockSerializer(serializers.ModelSerializer):
    time_start = serializers.TimeField(write_only=True)
    time_duration = serializers.TimeField(write_only=True)
    resource_name = serializers.ReadOnlyField(source="resource.name")
    class Meta:
        model = TimeBlock
        fields = [
            'id',
            'resource',
            'resource_name',
            'date',
            'time_start',
            'time_duration',
            'start_slot',
            'duration_slot',
        ]
        read_only_fields = [
            'start_slot',
            'duration_slot',
        ]
    def validate(self, attrs):
        time_start = attrs.pop('time_start', None)
        time_duration = attrs.pop('time_duration', None)
        attrs['start_slot'] = time_to_slots(time_start)
        attrs['duration_slot'] = time_to_slots(time_duration)

        return attrs
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(
            {
                'time_start': slot_to_time(instance.start_slot),
                'time_duration': slot_to_time(instance.duration_slot),
            }
        )
        return data
