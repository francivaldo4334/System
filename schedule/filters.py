import django_filters as filters

from schedule.models import Availability
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
    start_date = filters.DateTimeFilter(method='filter_date_range', required=True)
    end_date = filters.DateTimeFilter(method='filter_date_range', required=True)

    class Meta:
        model = Availability
        fields = ['resource']

    def filter_date_range(self, queryset, name, value):
        data = self.form.cleaned_data
        start_search = data.get('start_date')
        end_search = data.get('end_date')

        if not start_search and not end_search:
            return queryset

        q_objects = Q()

        if start_search:
            start_date_val = start_search.date()
            q_objects &= Q(valid_until__isnull=True) | Q(valid_until__gte=start_date_val)

        if end_search:
            end_date_val = end_search.date()
            # O início da disponibilidade deve ser antes ou igual ao fim do período buscado
            q_objects &= Q(valid_from__lte=end_date_val)

        return queryset.filter(q_objects).distinct()
