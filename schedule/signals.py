from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def atribuir_grupo_cliente(sender, instance, created, **kwargs):
    """Sinal que adiciona automaticamente o usuário recém-criado ao grupo 'client'."""
    if created:
        grupo_client, _ = Group.objects.get_or_create(name="CLIENT")
        instance.groups.add(grupo_client)
