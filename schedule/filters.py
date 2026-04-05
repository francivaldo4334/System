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
    # Definimos como 'method' para assumir o controle da query
    date_start = filters.DateFilter(method='filter_date_start', required=True)
    date_end = filters.DateFilter(method='filter_date_end', required=True)

    class Meta:
        model = Availability
        # Remova 'date_start' e 'date_end' de fields se eles não existem no model,
        # ou deixe vazio se só for usar esses dois filtros customizados.
        fields = []

    def filter_date_start(self, queryset, name, value):
        """
        Retorna itens onde o início da vigência é menor ou igual à data pesquisada.
        (O item começou antes ou no dia da pesquisa).
        """
        return queryset.filter(valid_from__lte=value)

    def filter_date_end(self, queryset, name, value):
        """
        Retorna itens onde o fim da vigência é maior ou igual à data pesquisada
        OU o fim da vigência é nulo (vigência aberta).
        """
        return queryset.filter(
            Q(valid_until__gte=value) | Q(valid_until__isnull=True)
        )
