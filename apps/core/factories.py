from factory.django import DjangoModelFactory

from .models import Dataset, Table


class DatasetFactory(DjangoModelFactory):
    class Meta:
        model = Dataset


class TableFactory(DjangoModelFactory):
    class Meta:
        model = Table
