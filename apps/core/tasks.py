import pandas as pd
import logging
from collections import defaultdict

from typing import Optional, Dict, List
from celery import shared_task

from apps.file.models import File
from apps.core.models import Table, Snapshot, Action, Join
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
    if len(clauses) == 1 and clauses[0]["operation"] == JOIN_CLAUSE_OPERATIONS.EQUAL:
        perform_hash_join(table, join_obj)
    else:
        logger.warning("Performing inefficient join since there are multiple clauses or non equal operations")
        perform_naive_join(table, join_obj)


def perform_hash_join(table: Table, join_obj: Join) -> Snapshot:
    assert table.joined_from == join_obj
    assert len(join_obj.clauses) == 1
    assert join_obj.clauses[0]["opertion"] == JOIN_CLAUSE_OPERATIONS.EQUAL

    source_stats = join_obj.source_table.data_column_stats
    target_stats = join_obj.target_table.data_column_stats
    source_cols = join_obj.source_table.data_columns
    target_cols = join_obj.target_table.data_columns
    source_rows = join_obj.source_table.data_rows
    target_rows = join_obj.target_table.data_rows

    clause = join_obj.clauses[0]
    source_col = clause["source_column"]
    target_col = clause["target_column"]

    # First create index on target columns which has the following structure
    # { value: [row_index1, row_index2] }
    target_index: Dict[str, List[int]] = create_column_index(target_col, target_rows)

    source_col_keys = set([x["key"] for x in source_cols])
    target_col_keys = set([x["key"] for x in target_cols])
    common_keys = source_col_keys.intersection(target_col_keys)

    """
    After joining, some column names might overlap In such case we
    leave the overlapping source column key as it is and only
    modify keys for target, for which we will just append _1.
    """
    # TODO: figure out and fix if appending _1 will maintain the uniqueness of column keys
    target_col_key_map = {
        key: key
        if key not in common_keys
        else key + "_1"  # Just append _1
        for key in target_col_keys
    }

    new_columns = [
        *source_cols,
        *[
            {**col, "key": target_col_key_map[col["key"]]}
            for col in target_cols
        ]
    ]
    new_stats = [
        *source_stats,
        *[
            {**stat, "key": target_col_key_map[stat["key"]]}
            for stat in target_stats
        ]
    ]

    def merge(source_row, target_row):
        new_target_row = {
            target_col_key_map[k]: v
            for k, v in target_row.items()
        }
        return {**source_row, **new_target_row}

    # Now iterate over source rows and perform join
    joined_rows: list = []
    for i, row in enumerate(source_rows):
        source_val = row[source_col]
        target_row_indices = target_index.get(source_val)
        if target_row_indices is None:
            continue
        for target_ind in target_row_indices:
            joined_row = merge(row, target_rows[target_ind])
            joined_rows.append(joined_row)

    # Create a snapshot
    return Snapshot.objects.create(
        table=table,
        version=1,
        data_rows=joined_rows,
        data_columns=new_columns,
        column_stats=new_stats,
    )


def create_column_index(target_col: str, rows: list) -> Dict[str, List[int]]:
    index: Dict[str, List[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        value = row[target_col]
        if value is None:
            continue
        index[str(value)].append(i)
    return index


def perform_naive_join(table: Table, join_obj: Join):
    assert table.joined_from == join_obj
    raise Exception("not implemented")
