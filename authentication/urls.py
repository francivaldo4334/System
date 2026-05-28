from django.urls import include, path
from rest_framework import routers

from authentication.views import EmailViewSet, waiting_email_confirmation

router = routers.SimpleRouter()
router.register('email', EmailViewSet, 'send_email')


urlpatterns = [
    path('waiting_confirmation', waiting_email_confirmation, name="waiting_email_confirmation"),
    path('', include(router.urls))
]
