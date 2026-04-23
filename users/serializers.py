from rest_framework import serializers

from users.models import ClientBadge


class ClientBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientBadge
        fields = [
            'user'
        ]
