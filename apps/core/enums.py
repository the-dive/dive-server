from utils.graphene.enums import (
    convert_enum_to_graphene_enum,
    get_enum_name_from_django_field,
)
from apps.core.models import Dataset, Table

DatasetStatusEnum = convert_enum_to_graphene_enum(
    Dataset.DatasetStatus, name="DatasetStatusEnum"
)
TableStatusEnum = convert_enum_to_graphene_enum(
    Table.TableStatus, name="TableStatusEnum"
)

enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in (
        (Dataset.status, DatasetStatusEnum),
        (Table.status, TableStatusEnum),
    )
}
