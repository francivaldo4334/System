from django.shortcuts import render
from rest_framework import viewsets

from feedback.models import Message
from feedback.serializers import MessageSerializer

# Create your views here.
class MessageViewSet(
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(
            created_by=self.request.user
        )
