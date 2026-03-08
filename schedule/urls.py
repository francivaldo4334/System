from django.urls import path

from schedule.views import schedule_view

urlpatterns = [
    path('', schedule_view, name='schedule_view')
]
