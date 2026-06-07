from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action

from feedback.models import Message, Response
from feedback.serializers import MessageSerializer

# Create your views here.
class MessageViewSet(
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    @action(["POST"], False)
    def mark_viewed(self, request):
        Response.objects.filter(
            feedback__created_by=self.request.user
        ).update(
            is_viewed=True,
        )
        return Response()

    def get_queryset(self):
        return super().get_queryset().filter(
            created_by=self.request.user
        )
