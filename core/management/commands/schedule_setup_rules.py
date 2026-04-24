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
    ],
    'FRONT_DESK': [],
    'PROFESSIONAL': [],
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
