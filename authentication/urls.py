from django.urls import include, path
from rest_framework import routers

from authentication.views import ConfirmEmailView, EmailViewSet, TriggerClientRemindersAPIView, waiting_email_confirmation

router = routers.SimpleRouter()
router.register('email', EmailViewSet, 'send_email')


urlpatterns = [
    path('waiting_confirmation', waiting_email_confirmation, name="waiting_email_confirmation"),
    path('confirm_email/<uuid:uuid>/<str:token>/',ConfirmEmailView.as_view(),name="confirm_email"),
    path('api/cron/send-reminders/', TriggerClientRemindersAPIView.as_view(), name='cron-client-reminders'),
    path('', include(router.urls))
]
