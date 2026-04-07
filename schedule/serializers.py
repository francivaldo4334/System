from rest_framework import serializers

from schedule.models import Assignment, Availability, Resource, Service


class ResourcesSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name")
    childrens = serializers.SerializerMethodField()
    class Meta:
        model = Resource
        fields = [
            'id',
            'label',
            'code',
            'is_selectable',
            'parent_id',
            'childrens',
        ]
    def get_childrens(self, obj):
        serializer = ResourcesSerializer(obj.childrens.all(), many=True)
        return serializer.data


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id',
            'title',
        ]


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
    time_from = serializers.TimeField(write_only=True, required=True)
    time_until = serializers.TimeField(write_only=True, required=False)
    duration = serializers.TimeField(write_only=True, required=True)
    interval = serializers.TimeField(write_only=True, required=True)
    resource_label = serializers.CharField(source="resource.name", read_only=True)

    class Meta:
        model = Availability
        fields = [
            "id", "description", "resource", "valid_from", "valid_until",
            "week", "time_from", "time_until", "duration", "interval",
            "rrule_params", "duration_slot", "interval_slot", "resource_label"
        ]
        extra_kwargs = {
            'rrule_params': {'read_only': True},
            'duration_slot': {'read_only': True},
            'interval_slot': {'read_only': True},
        }

    def _get_slot_count(self, init:int, end:int, duration: int, interval:int):
        return (end - init + interval) // (duration + interval)

    def validate(self, attrs):
        from datetime import datetime
        from dateutil.rrule import rrule, MINUTELY
        import re

        def get_slots(t):
            return (t.hour * 60 + t.minute) // 5

        week_days = attrs.get('week')
        time_from = attrs.get('time_from')
        time_until = attrs.get('time_until')
        valid_from = attrs.get('valid_from')
        valid_until = attrs.get('valid_until', None)
        duration_time = attrs.get('duration')
        interval_time = attrs.get('interval')

        slot_from = get_slots(time_from)
        slot_until = get_slots(time_until)
        slot_duration = get_slots(duration_time)
        slot_interval = get_slots(interval_time)

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

        for field in ['week', 'time_from', 'time_until', 'duration', 'interval']:
            attrs.pop(field, None)

        return attrs


class AvailabilityPresentationSerializer(serializers.ModelSerializer):
    occurrences = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ["id", "resource", "valid_from", "valid_until", "occurrences", "duration_slot"]

    def get_occurrences(self, obj):
        from datetime import datetime
        request = self.context.get("request", None)
        if not request:
            return None
        start = request.query_params.get("date_start")
        end = request.query_params.get("date_end")
        date_start = datetime.strptime(start, '%Y-%m-%d').date()
        date_end = datetime.strptime(end, '%Y-%m-%d').date()
        return obj.get_presentation(date_start, date_end)
