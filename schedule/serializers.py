from rest_framework import serializers

from schedule.models import Appointment, Assignment, Resource, Service


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


class AssignmentSerializer(serializers.ModelSerializer):
    class ServiceSerializer(serializers.ModelSerializer):
        class Meta:
            model = Service
            fields = ['id','title']
    class ResourceSerializer(serializers.ModelSerializer):
        class Meta:
            model = Resource
            fields = ['id','name']
    class AppointmentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Appointment
            fields = ['status']
    service = ServiceSerializer()
    resources = ResourceSerializer(many=True)
    appointment_set = AppointmentSerializer(many=True)
    class Meta:
        model = Assignment
        fields = [
            'id',
            'service',
            'resources',
            'appointment_set',
            'date',
            'start_slot',
            'duration_slot',
        ]
        # depth = 1
