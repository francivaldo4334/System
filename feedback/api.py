from django.urls import include, path
from rest_framework import routers

from feedback.views import MessageViewSet


router = routers.DefaultRouter()

router.register('',MessageViewSet, 'feedback-messages')

urlpatterns = [
    path('feedback',include(router.urls)), 
]
