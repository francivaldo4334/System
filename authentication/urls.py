from django.urls import path

from authentication.views import waiting_email_confirmation


urlpatterns = [
    path('waiting_confirmation', waiting_email_confirmation, name="waiting_email_confirmation")
]
