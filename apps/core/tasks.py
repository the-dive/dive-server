import pandas as pd
import logging

from typing import Optional
from celery import shared_task

from apps.file.models import File
from apps.core.models import Table, Snapshot, Action
from apps.core.utils import perform_hash_join, perform_naive_join
from dive.consts import JOIN_CLAUSE_OPERATIONS
from apps.core.actions.utils import get_composed_action_for_action_object
from utils.extraction import extract_data_from_excel

logger = logging.getLogger(__name__)


@shared_task
def extract_table_data(table_id: int):
    table: Optional[Table] = Table.objects.filter(id=table_id).first()
    if table is None:
        logger.warning(f"No such table(id: {table_id}) exists to extract data")
        return

    if table.source_type == File.Type.EXCEL:
        create_snapshot_for_table(table)
    else:
        raise Exception(f"Extraction for {table.source_type} not implemented")


def create_snapshot_for_table(table: Table) -> Optional[Snapshot]:
    pd_excel = pd.ExcelFile(table.dataset.file.file.path)
    extracted_data, err = extract_data_from_excel(
        pd_excel, table.original_name, table.properties, calculate_stats=True
    )
    if extracted_data is None:
        logger.warning(f"Error extracting data: {err}")
        return None

    return Snapshot.objects.create(
        table=table,
        version=1,
        data_rows=extracted_data["rows"],
        data_columns=extracted_data["columns"],
        column_stats=extracted_data["column_stats"],
    )


@shared_task
def calculate_column_stats_for_action(action_id: int):
    action_obj = Action.objects.filter(pk=action_id).first()
    if action_obj is None:
        logger.error(f"Calling stats calculation for inexistent action(id {action_id})")
        return

    action = get_composed_action_for_action_object(action_obj)
    _, _, _, column_stats = action.run_action()
    action_obj.table_column_stats = column_stats
    action_obj.save()


@shared_task
def perform_join(table_id: int):
    table = Table.objects.filter(id=table_id).first()
    if table is None:
        logger.error(f"Inexistent table(id: {table_id})")
        return
    join_obj = table.joined_from
    if join_obj is None:
        logger.error(f"Table(id: {table_id}) has no join info.")
        return

    clauses = join_obj.clauses
    is_join_with_equi_clause = (
        len(clauses) == 1 and
        clauses[0]["operation"] == JOIN_CLAUSE_OPERATIONS.EQUAL
    )
    if is_join_with_equi_clause:
        perform_hash_join(table)
    else:
        logger.warning("Performing inefficient join since there are multiple clauses or non equal operations")
        perform_naive_join(table, join_obj)
