import django_filters as filters

from schedule.models import Assignment, Availability, Resource, ResourceNotSelectable, ResourceSelectable, Service, ServiceResourceRelation
from django.db.models import Q


class AvailabilityFilterSet(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    class Meta:
        model = Availability
        fields = ["search"]

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(description__icontains=value)
        ).distinct()

class AvailabilityPresentationFilterSet(filters.FilterSet):
    date = filters.DateFilter(method='filter_date', required=True)

    class Meta:
        model = Availability
        fields = []

    def filter_date(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter_date_colision(value, value)

class ResourceFilterSet(filters.FilterSet):
    use_as_category = filters.BooleanFilter('is_selectable', exclude=True)
    is_selectable = filters.BooleanFilter('is_selectable')
    search = filters.CharFilter(method='filter_search')
    class Meta:
        model = Resource
        fields = ['parent']
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        ).distinct()

class ServiceFilterSet(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    class Meta:
        model = Service
        fields = []

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        ).distinct()

class ServiceRequirementsFilterSet(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    class Meta:
        model = ServiceResourceRelation
        fields = []

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(
                Q(service__title__icontains=value) |
                Q(service__description__icontains=value)
            ) |
            Q(resource_type__name__icontains=value)
        ).distinct()


class AssignmentFilterSet(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    resource = filters.ModelChoiceFilter(
        'resources',
        queryset=ResourceSelectable.objects.all(),
    )
    resource_category = filters.ModelChoiceFilter(
        'resources__parent',
        queryset=ResourceNotSelectable.objects.all(),
    )
    day = filters.DateFilter('date')
    class Meta:
        model = Assignment
        fields = [
            'service',
            'status'
        ]
    @property
    def qs(self):
        parent = super().qs
    
        status_value = self.data.get('status') # type:ignore
    
        if not status_value:
            return parent.visibles() # type:ignore
        
        return parent
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(
                Q(service__title__icontains=value) |
                Q(service__description__icontains=value)
            ) |
            Q(resources__name__icontains=value)
        ).distinct()
