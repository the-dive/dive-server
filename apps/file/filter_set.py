import django_filters

from utils.graphene.filters import MultipleInputFilter
from apps.file.models import File
from apps.file.enums import FileTypeEnum


class FileFilterSet(django_filters.FilterSet):
    file_statuses = MultipleInputFilter(FileTypeEnum, field_name="status")

    class Meta:
        model = File
        fields = ("file_statuses",)
