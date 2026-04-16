from rest_framework import serializers

from schedule.models import Assignment, Availability, Resource, ResourceNotSelectable, Service, ServiceResourceRelation
from django.utils.translation import gettext_lazy as _


class ResourcesSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name")
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
        error_messages={
            'required': _('Enter a valid value.')
        }
    )
    class Meta:
        model = Resource
        fields = [
            'id',
            'label',
            'code',
            'use_as_category',
            'parent',
            'parent_label',
            'is_selectable'
        ]
        read_only_fields = [
            'code',
            'is_selectable',
        ]
    def validate_parent(self, value):
        use_as_category = self.initial_data.get('use_as_category')
        print('here',use_as_category, value)
        if not value and not use_as_category:
            self.fail('required')
        return value
    def validate_use_as_category(self, value):
        return not value

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['use_as_category'] = not instance.is_selectable
        return representation
class ServiceResourceRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceResourceRelation
        fields = [
            'service',
            'resource_type',
            'quantity',
        ]

class ServiceSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="title")
    resources_label = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = [
            'id',
            'label',
            'description',
            'resources_label',
        ]
    def get_resources_label(self, obj):
        if not hasattr(obj, 'serviceresourcerelation_set'):
            return None;
        resource_labels = obj.serviceresourcerelation_set.values_list('resource_type__name', flat=True)
        return ','.join(resource_labels)

class AssignmentSerializer(serializers.ModelSerializer):
    class ServiceSerializer(serializers.ModelSerializer):
        class Meta:
            model = Service
            fields = ['id','title']
    class ResourceSerializer(serializers.ModelSerializer):
        class Meta:
            model = Resource
            fields = ['id','name']
    service = ServiceSerializer()
    resources = ResourceSerializer(many=True)
    class Meta:
        model = Assignment
        fields = [
            'id',
            'service',
            'resources',
            'date',
            'start_slot',
            'duration_slot',
        ]
        # depth = 1

# pyright: reportAttributeAccessIssue=false
class CreateAssigmentSerializer(AssignmentSerializer):
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )
    resources = serializers.PrimaryKeyRelatedField(
                queryset=Resource.objects.all(),
        many=True
    )

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
            print("rrule", rrule_str)
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

    def get_occurrences(self, obj):
        from datetime import datetime
        request = self.context.get("request", None)
        if not request:
            return None
        start = request.query_params.get("date")
        end = request.query_params.get("date")
        date_start = datetime.strptime(start, '%Y-%m-%d').date()
        date_end = datetime.strptime(end, '%Y-%m-%d').date()
        return obj.get_presentation(date_start, date_end)
