from django.urls import path

from schedule.views import home_view


urlpatterns = [
    path('', home_view, name="home-view")
]
