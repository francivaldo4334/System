from rest_framework import serializers

from schedule.models import Resource, Service


class ResourcesSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'id',
            'name',
            'code',
            'is_selectable',
            'children',
            'parent_id'
        ]

    def get_children(self, obj):
        serializer = ResourcesSerializer(obj.children.all(), many=True)
        return serializer.data

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id',
            'title',
        ]
