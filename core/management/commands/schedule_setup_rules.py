from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _

from schedule.models import ResourceNotSelectable

PERMISSION_GROUPS = {
    'OWNER': [
        'view_resource',
        'view_resourcenotselectable',
        'view_availability',
        'view_assignment',
        'view_service',
        'view_serviceresourcerelation',
        'view_appconfig',
        'view_customuser',
        'view_timeblock',

        'change_resource',
        'change_resourcenotselectable',
        'change_availability',
        'change_assignment',
        'change_service',
        'change_serviceresourcerelation',
        'change_appconfig',
        'change_customuser',
        'change_timeblock',

        'add_resource',
        'add_resourcenotselectable',
        'add_availability',
        'add_assignment',
        'add_service',
        'add_serviceresourcerelation',
        'add_appconfig',
        'add_customuser',
        'add_timeblock',

        'delete_resource',
        'delete_resourcenotselectable',
        'delete_availability',
        'delete_assignment',
        'delete_service',
        'delete_serviceresourcerelation',
        'delete_customuser',
        'delete_timeblock',

        'view_message',
        'add_message',
    ],
    'FRONT_DESK': [        
        'view_resource',
        'view_availability',
        'view_assignment',
        'view_service',
        'view_message',
        'add_message',
    ],
    'PROFESSIONAL': [
        'view_message',
        'add_message',
        
    ],
    'CLIENT': [
        'view_resource',
        'view_availability',
        'view_assignment',
        'view_service',
        'view_serviceresourcerelation',
        'view_appconfig',
        'view_customuser',

        'add_assignment',
        'change_assignment',
    ],
}

class Command(BaseCommand):
    help = "Gera um setup de Pemission Groups focado para uso do modulo de agenda"
    def handle(self, *args, **options):
        with atomic(): # type:ignore
            for group_name, rules in PERMISSION_GROUPS.items():
                group, created = Group.objects.get_or_create(name=group_name)
                permissions_to_add = []
                for rule in rules:
                    perm = Permission.objects.get(codename=rule)
                    permissions_to_add.append(perm)
                group.permissions.set(permissions_to_add)
                status = "Criado" if created else "Atualizado"
                self.stdout.write(self.style.SUCCESS(f'Gropo {group_name}: {status} com {len(permissions_to_add)} permissões.'))

            from django.apps import apps
            from django.conf import settings
            from django.contrib.contenttypes.models import ContentType
            user_model = apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
            content_type = ContentType.objects.get_for_model(user_model)
            client_type, c = ResourceNotSelectable.objects.get_or_create(
                code="client",
                defaults={
                    'is_selectable': False,
                    'name': _('Client'),
                    'content_type': content_type
                }
            )
