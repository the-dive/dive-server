import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene_django_extras import PageGraphqlPagination, DjangoObjectField

from utils.graphene.types import CustomDjangoListObjectType
from utils.graphene.fields import DjangoPaginatedListObjectField
from utils.graphene.enums import EnumDescription

from apps.core.models import (
    Dataset,
    Table,
)
from apps.core.filter_set import DatasetFilter


class TableType(DjangoObjectType):
    class Meta:
        model = Table
        only_fields = ("id", "name", "status")
        skip_registry = True

    status_display = EnumDescription(source="get_status_display")


class DatasetType(DjangoObjectType):
    class Meta:
        model = Dataset
        fields = "__all__"

    tables = DjangoListField(TableType)


class DatasetListType(CustomDjangoListObjectType):
    class Meta:
        model = Dataset
        filterset_class = DatasetFilter


class Query(graphene.ObjectType):
    dataset = DjangoObjectField(DatasetType)
    datasets = DjangoPaginatedListObjectField(
        DatasetListType,
        pagination=PageGraphqlPagination(page_size_query_param="pageSize"),
    )
