from rest_framework import serializers

from schedule.models import Appointment, Resource, Service


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            'id',
            'name',
            'code',
            'is_selectable',
            'parent_id'
        ]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id',
            'title',
        ]


class AssignmentSlotSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField(
        source="service.title",
        allow_null=True,
    )
    class Meta:
        model = Appointment
        fields = [
            'id',
            'status',
            'service_id',
            'service_title',
            'resources',
            'date',
            'start_slot',
            'duration_slot',
        ]
