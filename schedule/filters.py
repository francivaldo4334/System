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

    date_after = filters.DateFilter(field_name='date_after', method='filter_by_range')
    date_before = filters.DateFilter(field_name='date_before', method='filter_by_range')
    day = filters.DateFilter(method='filter_date')
    resource = filters.BaseInFilter('resources__id', method='filter_pass')
    resource_category = filters.BaseInFilter('resources__parent_id', method='filter_pass')

    def filter_pass(self, queryset, name, value):
        return queryset

    def filter_by_range(self, queryset, name, value):
        date_after = self.data.get('date_after')
        date_before = self.data.get('date_before')

        if not date_after or not date_before:
            return queryset

        if name == 'date_before':
            return queryset.filter_date_colision(date_after, date_before)
        
        return queryset

    class Meta:
        model = Availability
        fields = []

    def filter_date(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter_date_colision(value, value)

class AvailabilityPresentationAssignmentFilterSet(filters.FilterSet):
    date_after = filters.DateFilter(field_name='date_after', method='filter_by_range')
    date_before = filters.DateFilter(field_name='date_before', method='filter_by_range')
    day = filters.DateFilter(field_name='date')
    service = filters.NumberFilter()

    resource = filters.BaseInFilter('resources__id', method='filter_pass')
    resource_category = filters.BaseInFilter('resources__parent_id', method='filter_pass')

    def filter_by_range(self, queryset, name, value):
        date_after = self.data.get('date_after')
        date_before = self.data.get('date_before')

        if not date_after or not date_before:
            return queryset

        if name == 'date_before':
            return queryset.filter(
                date__gte=date_after,
                date__lte=date_before,
            )
        
        return queryset

    def filter_pass(self, queryset, name, value):
        return queryset

    class Meta:
        model = Assignment
        fields = ['date', 'service']

class ResourceFilterSet(filters.FilterSet):
    use_as_category = filters.BooleanFilter('is_selectable', exclude=True)
    is_selectable = filters.BooleanFilter('is_selectable')
    search = filters.CharFilter(method='filter_search')
    service = filters.NumberFilter('service__id')
    class Meta:
        model = Resource
        fields = ['parent','parent__code']
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
        fields = ['required_resources__code']

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
    resource = filters.BaseInFilter('resources__id')
    resource_category = filters.BaseInFilter('resources__parent_id')
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
