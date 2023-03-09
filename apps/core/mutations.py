from typing import Any

from django.db import transaction
import graphene
from graphene.types.generic import GenericScalar
from graphene_file_upload.scalars import Upload

from utils.graphene.error_types import (
    CustomErrorType,
    mutation_is_not_valid,
)
from utils.graphene.mutation import (
    generate_input_type_for_serializer,
    DiveMutationMixin,
)

from dive.consts import JOIN_CLAUSE_OPERATIONS
from apps.core.schema import DatasetType, TableType
from apps.core.actions.base import get_all_action_names
from apps.core.actions.utils import parse_raw_action
from apps.file.serializers import FileSerializer, File
from apps.core.utils import create_dataset_and_tables, perform_hash_join_

from utils.decorators import lift_mutate_with_instance
from .serializers import TablePropertiesSerializer, TableJoinSeralizer
from .models import Table, Action, Join
from .utils import apply_table_properties_and_extract_preview
from .tasks import extract_table_data, calculate_column_stats_for_action, perform_join
from .schema import KeyLabelType


TablePropertiesInputType = generate_input_type_for_serializer(
    "TablePropertiesInputType",
    TablePropertiesSerializer,
)
TableJoinInputType = generate_input_type_for_serializer(
    "TableJoinInputType", TableJoinSeralizer
)


class RowsColumnsType(graphene.ObjectType):
    rows = graphene.List(GenericScalar)
    columns = graphene.List(KeyLabelType)


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
        is_added_to_workspace = graphene.Boolean(required=True)
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    @lift_mutate_with_instance(Table)
    def mutate(instance, root, info, id, is_added_to_workspace):
        instance.is_added_to_workspace = is_added_to_workspace
        instance.save()
        extract_table_data.delay(instance.id)
        return AddTableToWorkSpace(result=instance, errors=None, ok=True)


class UpdateTableProperties(graphene.Mutation):
    class Arguments:
        data = TablePropertiesInputType(required=True)
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    @lift_mutate_with_instance(Table)
    def mutate(instance, root, info, id, data):
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
        apply_table_properties_and_extract_preview(instance)
        return UpdateTableProperties(result=instance, errors=None, ok=True)


class DeleteTableFromWorkspace(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    @lift_mutate_with_instance(Table)
    def mutate(instance, root, info, id):
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
    @lift_mutate_with_instance(Table)
    def mutate(instance, root, info, id):
        cloned_table = instance.clone()
        return DeleteTableFromWorkspace(result=cloned_table, errors=None, ok=True)


class RenameTable(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    @lift_mutate_with_instance(Table)
    def mutate(instance, root, info, id, name):
        instance.name = name
        instance.save(update_fields=["name"])
        return DeleteTableFromWorkspace(result=instance, errors=None, ok=True)


ActionEnum = graphene.Enum("ActionEnum", [(ac, ac) for ac in get_all_action_names()])


class ActionInputType(graphene.InputObjectType):
    action_name = graphene.Field(ActionEnum)
    params = graphene.List(graphene.String)


class PerformTableAction(graphene.Mutation):
    class Arguments:
        action = ActionInputType(required=True)
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    @lift_mutate_with_instance(Table)
    def mutate(table, root, info, id, action: Any):
        """
        Validate action and parameters and create an Action object if all valid
        """
        action_name = action["action_name"]
        params = action["params"]
        action = parse_raw_action(action_name, params, table)
        if action is None:
            errors = ["invalid action name"]
            return PerformTableAction(errors=errors, ok=False)
        elif action.is_valid is False:
            errors = [action.error]
            return PerformTableAction(errors=errors, ok=False)

        # Create action
        last_action = Action.objects.filter(table=table).order_by("-order").first()
        action_obj = Action.objects.create(
            table=table,
            action_name=action_name,
            parameters=params,
            order=last_action.order + 1 if last_action is not None else 1,
        )
        # Call background task to calculate the stats.
        transaction.on_commit(
            lambda: calculate_column_stats_for_action.delay(action_obj.id)
        )
        return PerformTableAction(result=table, errors=None, ok=True)


class TableJoinMutation(graphene.Mutation):
    class Arguments:
        data = TableJoinInputType(required=True)
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(TableType)

    @staticmethod
    @lift_mutate_with_instance(Table)
    def mutate(table, root, info, id, data: Any):
        target_table = data["target_table"]
        join_type = data["join_type"]
        clauses = data["clauses"]

        # create Join
        join = Join.objects.create(
            source_table=table,
            target_table=Table.objects.filter(id=target_table).first(),
            join_type=join_type,
            clauses=clauses,
        )

        # Create table from the joined
        joined_original_name = (
            join.source_table.name + " : " + "JOIN" + " : " + join.target_table.name
        )
        joined_table = Table.objects.create(
            # NOTE: what should be the dataset of the joined table?
            # It is not completely sure yet what the dataset should
            # be. For now we just keep the source table's dataset
            dataset=join.source_table.dataset,
            name=joined_original_name,
            original_name=joined_original_name,
            joined_from=join,
            is_added_to_workspace=join.source_table.is_added_to_workspace,
        )

        # call background task to perform join
        transaction.on_commit(lambda: perform_join.delay(joined_table.id))
        return TableJoinMutation(result=joined_table, errors=None, ok=True)


class JoinPreviewMutation(graphene.Mutation):
    class Arguments:
        data = TableJoinInputType(required=True)
        id = graphene.ID(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(RowsColumnsType)

    @staticmethod
    @lift_mutate_with_instance(Table)
    def mutate(source_table, root, info, id, data: Any):
        target_table_id = data["target_table"]
        join_type = data["join_type"]
        clauses = data["clauses"]
        target_table = Table.objects.get(id=target_table_id)

        is_join_with_equi_clause = (
            len(clauses) == 1
            and clauses[0]["operation"] == JOIN_CLAUSE_OPERATIONS.EQUAL
        )
        if is_join_with_equi_clause:
            new_cols, new_rows, _ = perform_hash_join_(
                clauses[0],
                source_table.preview_data,
                target_table.preview_data,
                join_type=join_type,
                conflicting_col_suffix=str(target_table.id),
            )
        else:
            return DiveMutationMixin(
                errors=[
                    dict(
                        field="nonFieldErrors",
                        messages=(
                            "This clause is not supported at the moment."
                            " Please use single inner join with equality clause."
                        ),
                    )
                ]
            )
        result = {
            "rows": new_rows,
            "columns": new_cols,
        }
        return JoinPreviewMutation(result=result, errors=None, ok=True)


class Mutation:
    create_dataset = CreateDataset.Field()
    add_table_to_workspace = AddTableToWorkSpace.Field()
    delete_table_from_workspace = DeleteTableFromWorkspace.Field()
    clone_table = CloneTable.Field()
    update_table_properties = UpdateTableProperties.Field()
    rename_table = RenameTable.Field()
    table_action = PerformTableAction.Field()
    table_join = TableJoinMutation.Field()
    join_preview = JoinPreviewMutation.Field()
