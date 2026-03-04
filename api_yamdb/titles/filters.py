import django_filters
from .models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр для произведений: связываем параметры URL с полями БД."""
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year', 'name')
