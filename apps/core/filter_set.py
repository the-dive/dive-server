import django_filters

from apps.core.models import Dataset


class DatasetFilter(django_filters.FilterSet):
    class Meta:
        model = Dataset
        fields = ()
