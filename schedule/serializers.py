from rest_framework import serializers

from schedule.models import Resource


class ResourcesSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'name',
            'code',
            'is_selectable',
            'children',
            'parent_id'
        ]

    def get_children(self, obj):
        serializer = ResourcesSerializer(obj.children.all(), many=True)
        return serializer.data
