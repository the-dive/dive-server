import django_filters

from apps.core.models import Dataset


class DatasetFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Dataset
        fields = ()
