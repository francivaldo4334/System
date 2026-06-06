from rest_framework import serializers

from feedback.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'text',
            'status',
            'category',
            'created',
            'modified',
            'created_by',
        ]
        read_only_fields = [
            'status',
            'created',
            'modified',
            'created_by',
        ]
    def save(self, **kwargs):
        request = self.context.get('request')
        user = request.user
        return super().save(**kwargs, created_by=user)
