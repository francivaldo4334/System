from rest_framework import serializers

from app.models import AppConfig

class AppConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConfig
        fields = [
            'company_image',
            'company_name',
            'background_image',
            'resource_slogs_visible_to_self_scheduling'
        ]
