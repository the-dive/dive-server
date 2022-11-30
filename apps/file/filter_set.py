import django_filters

from apps.file.models import File


class FileFilterSet(django_filters.FilterSet):
    class Meta:
        model = File
        fields = ()
