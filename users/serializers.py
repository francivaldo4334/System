from rest_framework import serializers

from users.models import CustomerBadge


class BadgeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    class Meta:
        model = CustomerBadge
        fields = [
            'full_name'
        ]
