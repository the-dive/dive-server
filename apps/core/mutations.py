import graphene
from graphene_file_upload.scalars import Upload

from utils.graphene.error_types import (
    CustomErrorType,
    mutation_is_not_valid,
)
from utils.graphene.mutation import (
    generate_input_type_for_serializer,
    DiveMutationMixin,
)

from apps.core.schema import DatasetType, TableType
from apps.file.serializers import FileSerializer, File
from apps.file.utils import create_dataset_and_tables

from .serializers import TableUpdateSerializer
from .models import Table


TableInputType = generate_input_type_for_serializer(
    'TableInputType',
    TableUpdateSerializer,
)


class CreateDatasetInputType(graphene.InputObjectType):
    file = Upload(required=True)


class CreateDataset(graphene.Mutation):
    class Arguments:
        data = CreateDatasetInputType(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(DatasetType)

    @staticmethod
    def mutate(root, info, data):
        serializer = FileSerializer(
            data=data, context={"request": info.context.request}
        )
        if errors := mutation_is_not_valid(serializer):
            return CreateDataset(errors=errors, ok=False)
        file_obj: File = serializer.save()
        dataset = create_dataset_and_tables(file_obj)
        # TODO: send in background to extract
        return CreateDataset(result=dataset, errors=None, ok=True)


class UpdateTable(DiveMutationMixin):
    class Arguments:
        data = TableInputType(required=True)
        id = graphene.ID()

    model = Table
    serializer_class = TableUpdateSerializer
    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)


class Mutation:
    create_dataset = CreateDataset.Field()
    update_table = UpdateTable.Field()
