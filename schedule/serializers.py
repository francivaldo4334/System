from django.db import transaction
from rest_framework import serializers

from schedule.models import Assignment, Availability, Resource, ResourceNotSelectable, ResourceSelectable, Service, ServiceResourceRelation
from django.utils.translation import gettext_lazy as _

from schedule.utils import ReourceQuantityNotEguals, ResourceNotAllowed, ResourceOcuppied, ServiceIsRequired


class ResourceSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    use_as_category = serializers.BooleanField(
        source="is_selectable",
        default=False,
    )
    parent_label = serializers.CharField(source='parent.name',
                                         allow_null=True,
                                         read_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=ResourceNotSelectable.objects.all(),
        required=False,
    )
    class Meta:
        model = Resource
        fields = [
            'id',
            'label',
            'name',
            'code',
            'use_as_category',
            'parent',
            'parent_label',
            'is_selectable'
        ]
        write_only_fields = [
            'name',
        ]
        read_only_fields = [
            'code',
            'is_selectable',
        ]
    def get_label(self, obj: Resource):
        if obj.parent:
            prefix = self.get_label(obj.parent) # type:ignore
            return  f'{prefix} / {obj.name}'
        return obj.name

    def validate(self, attrs):
        is_selectable = attrs.get('is_selectable', False)
        parent = attrs.get('parent', None)
        if not parent and is_selectable:
            raise serializers.ValidationError(
                {'parent': _('This field is required.')}
            )
        return super().validate(attrs)

    def validate_use_as_category(self, value):
        return not value

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['use_as_category'] = not instance.is_selectable
        return representation

class ServiceResourceRelationSerializer(serializers.ModelSerializer):
    service_label = serializers.ReadOnlyField(source='service.title')
    resource_type_label = serializers.ReadOnlyField(source='resource_type.name')
    class Meta:
        model = ServiceResourceRelation
        fields = [
            'id',
            'service',
            'resource_type',
            'quantity',
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
    class Meta:
        model = Service
        fields = [
            'id',
            'label',
            'description',
            'required_resources_label',
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
    service_name = serializers.CharField(source="service.title")
    resource_names = serializers.SerializerMethodField()

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
        ]
        read_only_fields = [
            'duration_slot',
        ]

    def get_resource_names(self, obj):
        return [f'{r.parent.name}/{r.name}' for r in obj.resources.all()]

    def create(self, validated_data):
        request = self.context.get('request')
        availability = validated_data.pop('availability')
        validated_data['duration_slot'] = availability.duration_slot        
        validated_data['created_by'] = getattr(request,'user')
        resources = validated_data.pop('resources')
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
        'resourcenotallowed': _('One or more selected resources are not allowed for this service type.'),
        'reourcequantitynoteguals': _('The provided resource quantity does not match the requirement for this service.'),
        'resourceocuppied': _('One or more selected resources are already occupied at the requested time.'),
        'serviceisrequired': _('Service is required for creating this assignment.'),
    }
    @transaction.atomic()
    def create(self, validated_data):
        try:
            instance:Assignment = super().create(validated_data)
            instance.state.confirm()
            return instance
        except ReourceQuantityNotEguals:
            raise self.fail('reourcequantitynoteguals')
        except ResourceNotAllowed:
            raise self.fail('resourcenotallowed')
        except ResourceOcuppied:
            raise self.fail('resourceocuppied')
        except ServiceIsRequired:
            raise self.fail('serviceisrequired')
        

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

    def get_occurrences(self, obj: Availability):
        from datetime import datetime

        request = self.context.get("request")
        assignments = self.context.get('assignments', [])
        exclude_times = set()
        for assignment in assignments:
            hours, minutes = divmod(assignment.start_slot * 5, 60)
            exclude_times.add(f'{hours:02d}:{minutes:02d}')

        date_str = request.query_params.get("date")
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        occurences = obj.get_occurrences(target_date, target_date)
        return [
            it for it in occurences
            if it.strftime('%H:%M') not in exclude_times
        ]
