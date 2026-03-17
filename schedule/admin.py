from django.contrib import admin
from schedule.models import *

# Register your models here.
admin.site.register(Resource)
admin.site.register(Availability)
admin.site.register(Service)
admin.site.register(ServiceResourceRelation)
