from rest_framework import serializers

from app.models import AppConfig

class AppConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConfig
        fields = [
            'company_image',
            'company_name',
            'background_image',
        ]
 
