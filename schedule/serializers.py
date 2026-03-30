from rest_framework import serializers

from schedule.models import Assignment, Availability, Resource, Service


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            'id',
            'name',
            'code',
            'is_selectable',
            'parent_id',
            'childrens',
        ]
        depth=1


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
    class Meta:
        model = Availability
        fields = [
            "id",
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
