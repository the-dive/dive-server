import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene.types.generic import GenericScalar
from graphene_django_extras import (
    PageGraphqlPagination,
    DjangoObjectField,
)

from utils.graphene.types import CustomDjangoListObjectType
from utils.graphene.fields import DjangoPaginatedListObjectField
from utils.graphene.enums import EnumDescription

from apps.core.models import (
    Dataset,
    Table,
    Join,
)
from apps.core.filter_set import DatasetFilter, TableFilter
from dive.consts import (
    TABLE_HEADER_LEVELS,
    LANGUAGES,
    TIMEZONES,
    COLUMN_TYPES,
)


class TablePropertiesType(graphene.ObjectType):
    """
    Type for table properties which is a json field in database
    """

    header_level = graphene.String()
    timezone = graphene.String()
    language = graphene.String()
    trim_whitespaces = graphene.Boolean()
    treat_these_as_na = graphene.String()

    @staticmethod
    def resolve_header_level(root, info, **kwargs):
        return root.get("headerLevel")

    @staticmethod
    def resolve_timezone(root, info, **kwargs):
        return root.get("timezone")

    @staticmethod
    def resolve_language(root, info, **kwargs):
        return root.get("language")

    @staticmethod
    def resolve_trim_whitespaces(root, info, **kwargs):
        return root.get("trimWhitespaces")

    @staticmethod
    def resolve_treat_these_as_na(root, info, **kwargs):
        return root.get("treatTheseAsNa")


class TableColumnStatsType(graphene.ObjectType):
    key = graphene.String(required=True)
    type = graphene.String(required=True)
    label = graphene.String(required=True)
    na_count = graphene.Int(required=True)
    max_length = graphene.Int()
    min_length = graphene.Int()
    total_count = graphene.Int(required=True)
    unique_count = graphene.Int()
    max = graphene.Float()
    min = graphene.Float()
    median = graphene.Float()
    std_deviation = graphene.Float()
    mean = graphene.Float()


class JoinType(DjangoObjectType):
    class Meta:
        model = Join
        fields = ("id", "clauses", "source_table", "target_table", "join_type")


class TableType(DjangoObjectType):
    class Meta:
        model = Table
        fields = (
            "id",
            "name",
            "status",
            "is_added_to_workspace",
            "preview_data",
            "properties",
            "cloned_from",
            "data_column_stats",
            "data_rows",
            "joined_from",
            "original_name",
        )

    status_display = EnumDescription(source="get_status_display")
    preview_data = GenericScalar()
    properties = graphene.Field(TablePropertiesType)
    data_column_stats = graphene.List(TableColumnStatsType, source="data_column_stats")
    data_rows = GenericScalar(source="data_rows")
    rows_count = graphene.Int()
    columns_count = graphene.Int()

    @staticmethod
    def resolve_rows_count(root, info, **kwargs):
        return len(root.data_rows)

    @staticmethod
    def resolve_columns_count(root, info, **kwargs):
        return len(root.data_columns)


class TableListType(CustomDjangoListObjectType):
    class Meta:
        model = Table
        filterset_class = TableFilter


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
        return Table.objects.filter(dataset=root.id).order_by("-created_at")


class DatasetDetailType(DatasetType):
    class Meta:
        model = Dataset
        fields = "__all__"


class DatasetListType(CustomDjangoListObjectType):
    class Meta:
        model = Dataset
        filterset_class = DatasetFilter


class KeyLabelType(graphene.ObjectType):
    key = graphene.String(required=True)
    label = graphene.String(required=True)


class ColumnPropertiesOptionsType(graphene.ObjectType):
    column_types = graphene.List(KeyLabelType)

    def resolve_column_types(self, info):
        output = []
        for d in COLUMN_TYPES:
            output.append(
                KeyLabelType(
                    key=d["key"],
                    label=d["label"],
                )
            )
        return output


class TablePropertiesOptionsType(graphene.ObjectType):
    """
    Type for table properties options.
    For example: table properties has following keys: headerLevel, time_zone, etc
    """

    header_levels = graphene.List(KeyLabelType)
    languages = graphene.List(KeyLabelType)
    timezones = graphene.List(KeyLabelType)

    def resolve_header_levels(self, info):
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

    def resolve_timezones(self, info):
        return [KeyLabelType(key=tz["key"], label=tz["label"]) for tz in TIMEZONES]


class PropertiesOptionsType(graphene.ObjectType):
    table = graphene.Field(TablePropertiesOptionsType)
    column = graphene.Field(ColumnPropertiesOptionsType)

    def resolve_table(self, info):
        return TablePropertiesOptionsType()

    def resolve_column(self, info):
        return ColumnPropertiesOptionsType()


class Query(graphene.ObjectType):
    dataset = DjangoObjectField(DatasetDetailType)
    datasets = DjangoPaginatedListObjectField(
        DatasetListType,
        pagination=PageGraphqlPagination(page_size_query_param="pageSize"),
    )
    properties_options = graphene.Field(PropertiesOptionsType)
    table = DjangoObjectField(TableType)
    tables = DjangoPaginatedListObjectField(
        TableListType,
        pagination=PageGraphqlPagination(page_size_query_param="pageSize"),
    )

    def resolve_properties_options(self, info):
        return PropertiesOptionsType()
