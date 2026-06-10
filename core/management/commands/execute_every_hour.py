from django.core.management.base import BaseCommand

from authentication.services import TriggerReminders

class Command(BaseCommand):
    def handle(self, *args, **options):
        ...
        # TriggerReminders().trigger()
