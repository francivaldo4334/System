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
        depth = 1
