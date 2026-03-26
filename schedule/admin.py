from django.contrib import admin
from schedule.models import *

# Register your models here.
@admin.register(Assignment)
class AssignmentSlotAdmin(admin.ModelAdmin):
    actions = [        
        'confirm',
        'start',
        'finish',
        'cancel',
    ]

    @admin.action(description="confirm")
    def confirm(self, request, queryset):
        for obj in queryset:
            obj.state.confirm()
    @admin.action(description="start")
    def start(self, request, queryset):
        for obj in queryset:
            obj.state.start()
    @admin.action(description="finish")
    def finish(self, request, queryset):
        for obj in queryset:
            obj.state.finish()
    @admin.action(description="cancel")
    def cancel(self, request, queryset):
        for obj in queryset:
            obj.state.cancel()
admin.site.register(Resource)
admin.site.register(Availability)
admin.site.register(Service)
admin.site.register(ServiceResourceRelation)
admin.site.register(ResourceOccupation)
