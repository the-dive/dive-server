from django.utils.translation import gettext

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

from .serializers import TableUpdateSerializer, TablePropertiesSerializer
from .models import Table
from .utils import apply_properties_to_table


TablePropertiesInputType = generate_input_type_for_serializer(
    "TablePropertiesInputType",
    TablePropertiesSerializer,
)


class TableInputType(graphene.InputObjectType):
    is_added_to_workspace = graphene.Boolean(required=True)


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
        return CreateDataset(result=dataset, errors=None, ok=True)


class AddTableToWorkSpace(DiveMutationMixin):
    class Arguments:
        data = TableInputType(required=True)
        id = graphene.ID(required=True)

    model = Table
    serializer_class = TableUpdateSerializer
    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)


class UpdateTableProperties(graphene.Mutation):
    class Arguments:
        data = TablePropertiesInputType(required=True)
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    def mutate(root, info, id, data):
        try:
            instance = Table.objects.get(id=id)
        except Table.DoesNotExist:
            return DeleteTableFromWorkspace(
                errors=[
                    dict(
                        field="nonFieldErrors",
                        messages=gettext("Table does not exist."),
                    )
                ]
            )
        serializer = TablePropertiesSerializer(
            data=data, context={"request": info.context.request}
        )
        if errors := mutation_is_not_valid(serializer):
            return UpdateTableProperties(
                errors=errors,
                ok=False,
            )
        instance.properties = serializer.data
        instance.save()
        # call apply tabel properties
        apply_properties_to_table()
        return UpdateTableProperties(result=instance, errors=None, ok=True)


class DeleteTableFromWorkspace(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    def mutate(root, info, id):
        try:
            instance = Table.objects.get(id=id)
        except Table.DoesNotExist:
            return DeleteTableFromWorkspace(
                errors=[
                    dict(
                        field="nonFieldErrors",
                        messages=gettext("Table does not exist."),
                    )
                ]
            )
        instance.is_added_to_workspace = False
        instance.save()
        return DeleteTableFromWorkspace(result=instance, errors=None, ok=True)


class CloneTable(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    def mutate(root, info, id):
        try:
            instance = Table.objects.get(id=id)
        except Table.DoesNotExist:
            return DeleteTableFromWorkspace(
                errors=[
                    dict(
                        field="nonFieldErrors",
                        messages=gettext("Table does not exist."),
                    )
                ]
            )
        cloned_table = instance.clone()
        return DeleteTableFromWorkspace(result=cloned_table, errors=None, ok=True)


class Mutation:
    create_dataset = CreateDataset.Field()
    add_table_to_workspace = AddTableToWorkSpace.Field()
    delete_table_from_workspace = DeleteTableFromWorkspace.Field()
    clone_table = CloneTable.Field()
    update_table_properties = UpdateTableProperties.Field()
