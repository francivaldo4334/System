from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def atribuir_grupo_cliente(sender, instance, created, **kwargs):
    if created:
        # Certifique-se de que o grupo 'Clientes' já existe no banco
        grupo_cliente, _ = Group.objects.get_or_create(name="CLIENT")
        instance.groups.add(grupo_cliente)
