from rest_framework import serializers

from feedback.models import Message, Response


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = [
            'text',
            'is_viewed',
            'created',
        ]


class MessageSerializer(serializers.ModelSerializer):
    response_set = ResponseSerializer(many=True)
    class Meta:
        model = Message
        fields = [
            'text',
            'status',
            'category',
            'created',
            'modified',
            'created_by',
            'response_set',
        ]
        read_only_fields = [
            'status',
            'created',
            'modified',
            'created_by',
            'response_set',
        ]
    def save(self, **kwargs):
        request = self.context.get('request')
        user = request.user
        return super().save(**kwargs, created_by=user)
