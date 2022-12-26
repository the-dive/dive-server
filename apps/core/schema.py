import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene.types.generic import GenericScalar
from graphene_django_extras import PageGraphqlPagination, DjangoObjectField

from utils.graphene.types import CustomDjangoListObjectType
from utils.graphene.fields import DjangoPaginatedListObjectField
from utils.graphene.enums import EnumDescription

from apps.core.models import (
    Dataset,
    Table,
)
from apps.core.filter_set import DatasetFilter
from dive.consts import TABLE_HEADER_LEVELS, LANGUAGES, TIMEZONES


class TableType(DjangoObjectType):
    preview_data = GenericScalar()

    class Meta:
        model = Table
        fields = ("id", "name", "status", "is_added_to_workspace", "preview_data", "properties")
        skip_registry = True

    status_display = EnumDescription(source="get_status_display")


class DatasetType(DjangoObjectType):
    class Meta:
        model = Dataset
        fields = (
            "id",
            "name",
            "status",
        )
        skip_registry = True

    tables = DjangoListField(TableType)
    file = graphene.ID(source="file_id", required=True)
    status_display = EnumDescription(source="get_status_display")

    @staticmethod
    def resolve_tables(root, info, **kwargs):
        return Table.objects.filter(dataset=root.id)


class DatasetDetailType(DatasetType):
    class Meta:
        model = Dataset
        fields = "__all__"


class DatasetListType(CustomDjangoListObjectType):
    class Meta:
        model = Dataset
        filterset_class = DatasetFilter


class KeyLabelType(graphene.ObjectType):
    key = graphene.String()
    label = graphene.String()


class TablePropertiesType(graphene.ObjectType):
    headers = graphene.List(KeyLabelType)
    languages = graphene.List(KeyLabelType)
    time_zones = graphene.List(KeyLabelType)

    def resolve_headers(self, info):
        output = []
        for d in TABLE_HEADER_LEVELS:
            output.append(
                KeyLabelType(
                    key=d["key"],
                    label=d["label"],
                )
            )
        return output

    def resolve_languages(self, info):
        output = []
        for d in LANGUAGES:
            output.append(
                KeyLabelType(
                    key=d[0],
                    label=d[1],
                )
            )
        return output

    def resolve_time_zones(self, info):
        return [
            KeyLabelType(key=tz["key"], label=tz["label"])
            for tz in TIMEZONES
        ]


class PropertiesType(graphene.ObjectType):
    table = graphene.Field(TablePropertiesType)
    # column = graphene.Field(ColumnPropertiesType)

    def resolve_table(self, info):
        return TablePropertiesType()


class Query(graphene.ObjectType):
    dataset = DjangoObjectField(DatasetDetailType)
    datasets = DjangoPaginatedListObjectField(
        DatasetListType,
        pagination=PageGraphqlPagination(page_size_query_param="pageSize"),
    )
    properties = graphene.Field(PropertiesType)
    table = DjangoObjectField(TableType)

    def resolve_properties(self, info):
        return PropertiesType()
