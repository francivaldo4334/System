from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime, timedelta

from authentication.services import TriggerReminders

@shared_task
def send_appointment_reminder():
    count = TriggerReminders().appointments()
    return f"{count} e-mails enviados."

@shared_task
def send_availability_reminder():
    count = TriggerReminders().appointments()
    return f"{count} e-mails enviados."
