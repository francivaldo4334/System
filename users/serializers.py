from rest_framework import serializers

from users.models import ClientBadge


class ClientBadgeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    class Meta:
        model = ClientBadge
        fields = [
            'full_name'
        ]
