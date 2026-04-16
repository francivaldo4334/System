import django_filters as filters

from schedule.models import Availability, Resource
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
            Q(description__icontains=value) | 
            Q(resource__name__icontains=value)
        ).distinct()

class AvailabilityPresentationFilterSet(filters.FilterSet):
    date = filters.DateFilter(method='filter_date', required=True)

    class Meta:
        model = Availability
        fields = []

    def filter_date(self, queryset, name, value):
        return queryset.filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=value),
            valid_from__lte=value,
        )

class ResourceFilterSet(filters.FilterSet):
    use_as_category = filters.BooleanFilter('is_selectable', exclude=True)
    is_selectable = filters.BooleanFilter('is_selectable')
    search = filters.CharFilter(method='filter_search')
    class Meta:
        model = Resource
        fields = []
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        ).distinct()
