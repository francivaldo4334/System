from django.contrib import admin

from feedback.models import Message, Response

# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    pass
