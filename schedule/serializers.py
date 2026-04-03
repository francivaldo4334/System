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

# {
#     "resource_type": "1",
#     "resource": "1",
#     "valid_from": "2026-04-03",
#     "valid_until": "2026-04-03",
#     "week": "5",
#     "time_from": "08:00",
#     "time_until": "17:00",
#     "duration": "00:30",
#     "interval": "00:10",
#     "description": " teste"
# }
#
class AvailabilitySerializer(serializers.ModelSerializer):
    week = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                ("1","MO"),
                ("2","TU"),
                ("3","WE"),
                ("4","TH"),
                ("5","FR"),
                ("6","SA"),
                ("7","SU"),
            ],
            write_only=True,
        )
    )
    time_from = serializers.TimeField(write_only=True)
    time_until = serializers.TimeField(write_only=True)
    duration = serializers.TimeField(write_only=True)
    interval = serializers.TimeField(write_only=True)
    def validate(self, attrs):
        print("attrs[]")
        return super().validate(attrs)
    class Meta:
        model = Availability
        fields = [
            "id",
            "description",
            "resource",
            "valid_from",
            "valid_until",
            "week",
            "time_from",
            "time_until",
            "duration",
            "interval",
        ]

class _AvailabilitySerializer(serializers.ModelSerializer):
    rrule_params = serializers.RegexField(
        regex=r"^DTSTART:\d{8}T\d{6}\nRRULE:FREQ=MINUTELY;UNTIL=\d{8}T\d{6}Z?;INTERVAL=\d+;BYDAY=[A-Z,]+$"
    )
    default_error_messages = {
        "not_match_interval": {
            "rrule_params":"O INTERVAL da RRULE corresponde a soma dos parametros interval e duration"
        },
        "valid_until_gt_valid_from": {
            "valid_until": "Data final não pode ser menor que a data de inicio"
        }
    }
    class Meta:
        model = Availability
        fields = [
            "id",
            "description",
            "resource",
            "rrule_params",
            "duration_slot",
            "interval_slot",
            "valid_until",
            "valid_from",
        ]
        read_only_fields = [
            "valid_from",
        ]
    def validate(self, attrs):
        from dateutil.rrule import rrulestr,rruleset
        rule_obj = rrulestr(attrs["rrule_params"])
        r = rule_obj._rrule[0] if isinstance(rule_obj, rruleset) else rule_obj
        dtstart = r._dtstart
        interval_rrule = r._interval
        interval_in_minutes = (attrs["duration_slot"] + attrs["interval_slot"]) * 5
        if interval_rrule != interval_in_minutes:
            self.fail("not_match_interval")
        if attrs.get("valid_until", None) and dtstart.date() > attrs["valid_until"]:
            self.fail("valid_until_gt_valid_from")
        return attrs
