import factory
from factory.django import DjangoModelFactory

from .models import Dataset, Table, Snapshot, Join


class DatasetFactory(DjangoModelFactory):
    class Meta:
        model = Dataset


class TableFactory(DjangoModelFactory):
    name = factory.fuzzy.FuzzyText()
    original_name = factory.fuzzy.FuzzyText()

    class Meta:
        model = Table


class SnapshotFactory(DjangoModelFactory):
    class Meta:
        model = Snapshot


class JoinFactory(DjangoModelFactory):
    class Meta:
        model = Join
