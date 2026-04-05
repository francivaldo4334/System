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
            choices=[
                ("1", "MO"), ("2", "TU"), ("3", "WE"), ("4", "TH"),
                ("5", "FR"), ("6", "SA"), ("7", "SU"),
            ],
        ),
        write_only=True,
        required=True
    )
    time_from = serializers.TimeField(write_only=True, required=True)
    time_until = serializers.TimeField(write_only=True, required=True)
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

    def validate(self, attrs):
        from datetime import datetime

        week_days = attrs.get('week')
        time_from = attrs.get('time_from')
        time_until = attrs.get('time_until')
        valid_from = attrs.get('valid_from')
        duration_time = attrs.get('duration')
        interval_time = attrs.get('interval')
        def get_slots(t):
            return (t.hour * 60 + t.minute) // 5
        duration_slots = get_slots(duration_time)
        interval_slots = get_slots(interval_time)
        total_interval_minutes = (duration_slots + interval_slots) * 5
        day_map = {"1": "MO", "2": "TU", "3": "WE", "4": "TH", "5": "FR", "6": "SA", "7": "SU"}
        days_str = ",".join([day_map[d] for d in week_days])
        
        dt_start = datetime.combine(valid_from, time_from).strftime("%Y%m%dT%H%M%S")
        until_str = datetime.combine(valid_from, time_until).strftime("%Y%m%dT%H%M%S")
        print(dt_start, until_str)
        rrule_string = (
            f"DTSTART:{dt_start}\n"
            f"RRULE:FREQ=MINUTELY;UNTIL={until_str};"
            f"INTERVAL={total_interval_minutes};BYDAY={days_str}"
        )
        attrs['rrule_params'] = rrule_string
        attrs['duration_slot'] = duration_slots
        attrs['interval_slot'] = interval_slots
        for field in ['week', 'time_from', 'time_until', 'duration', 'interval']:
            attrs.pop(field, None)

        return attrs


class AvailabilityPresentationSerializer(serializers.ModelSerializer):
    occurrences = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ["id", "occurrences"]

    def get_occurrences(self, obj):
        request = self.context.get("request", None)
        if not request:
            return None
        start = request.query_params.get("start_date")
        end = request.query_params.get("end_date")

        return obj.get_presentation(start, end)
