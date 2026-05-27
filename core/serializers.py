from rest_framework import serializers
from django.apps import apps
from django.conf import settings

UserModel = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source="get_full_name")
    class Meta:
        model = UserModel
        fields = [
            'id',  # Recomendado incluir o ID para identificação nas respostas
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'full_name',
        ]
        extra_kwargs = {
            'password': {
                'required': False,
                'write_only': True,  # Garante que a senha nunca seja retornada no GET
                'style': {'input_type': 'password'}  # Melhora a interface navegável do DRF
            }
        }

    def create(self, validated_data):
        # Remove a senha dos dados validados para tratá-la separadamente
        password = validated_data.pop('password', None)
        # Cria a instância do usuário sem a senha primeiro
        user = super().create(validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user

    def update(self, instance, validated_data):
        # Trata a atualização de senha se ela for enviada
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user
