import django_filters as filters

from schedule.models import AssignmentSlot


class AssignmentSlotFilterSet(filters.FilterSet):
    class Meta:
        model = AssignmentSlot
        fields = {
            'date':['gte', 'lte', 'exact'],
            'status': ['exact'],
            'service': ['exact', 'in'],
            'resources': ['exact', 'in'],
        }
