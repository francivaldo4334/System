from django.urls import include, path
from rest_framework import routers

from authentication.views import EmailViewSet, TriggerClientRemindersView, waiting_email_confirmation

router = routers.SimpleRouter()
router.register('email', EmailViewSet, 'send_email')


urlpatterns = [
    path('waiting_confirmation', waiting_email_confirmation, name="waiting_email_confirmation"),
    path('api/cron/send-reminders/', TriggerClientRemindersView.as_view(), name='cron-client-reminders'),
    path('', include(router.urls))
]
