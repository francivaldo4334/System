from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.transaction import atomic

PERMISSION_GROUPS = {
    'OWNER': [
        'view_resource',
        'view_availability',
        'view_assignment',
        'view_service',
        'view_serviceresourcerelation',
        'view_appconfig',

        'change_resource',
        'change_availability',
        'change_assignment',
        'change_service',
        'change_serviceresourcerelation',
        'change_appconfig',

        'add_resource',
        'add_availability',
        'add_assignment',
        'add_service',
        'add_serviceresourcerelation',
        'add_appconfig',

        'delete_resource',
        'delete_availability',
        'delete_assignment',
        'delete_service',
        'delete_serviceresourcerelation',
    ],
    'FRONT_DESK': [        
        'view_resource',
        'view_availability',
        'view_assignment',
        'view_service',
    ],
    'PROFESSIONAL': [],
    'CLIENT': [
        'view_appconfig',
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
