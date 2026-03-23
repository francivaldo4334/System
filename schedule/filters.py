import django_filters as filters

from schedule.models import Appointment


class AssignmentSlotFilterSet(filters.FilterSet):
    class Meta:
        model = Appointment
        fields = {
            'date':['gte', 'lte', 'exact'],
            'status': ['exact'],
            'service': ['exact', 'in'],
            'resources': ['exact', 'in'],
        }
