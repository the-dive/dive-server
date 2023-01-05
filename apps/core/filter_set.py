import django_filters

from apps.core.models import Dataset, Table
from utils.graphene.filters import MultipleInputFilter
from apps.core.enums import TableStatusEnum


class DatasetFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Dataset
        fields = ("search",)


class TableFilter(django_filters.FilterSet):
    is_added_to_workspace = django_filters.BooleanFilter(
        method="filter_is_added_to_workspace"
    )
    statuses = MultipleInputFilter(TableStatusEnum, field_name="status")

    class Meta:
        models = Table
        fields = ("is_added_to_workspace", "statuses")

    def filter_is_added_to_workspace(self, qs, name, value):
        if value is True:
            return qs.filter(is_added_to_workspace=True)
        elif value is False:
            return qs.filter(is_added_to_workspace=False)
        return qs
