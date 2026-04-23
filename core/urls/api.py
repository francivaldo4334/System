from django.urls import path, include

urlpatterns = [
    path('', include('schedule.api')),
    path('', include('users.api')),
]
