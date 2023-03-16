from typing import List, Dict, Tuple, Any
from collections import defaultdict
import os
import pandas as pd
import logging

from django.db import transaction

from dive.consts import JOIN_CLAUSE_OPERATIONS
from apps.file.models import File
from apps.core.models import Table, Dataset, Join, Snapshot
from apps.core.validators import get_default_table_properties
from utils.extraction import extract_preview_data_from_excel
from utils.common import get_file_extension

logger = logging.getLogger(__name__)


def apply_table_properties_and_extract_preview(table: Table):
    if table.dataset.file.file_type == File.Type.EXCEL:
        pd_excel = pd.ExcelFile(table.dataset.file.file.path)
        preview_data, err = extract_preview_data_from_excel(
            pd_excel, table.original_name, table.properties
        )
    else:
        raise Exception("Extraction not implemented for filetypes other than excel")
    table.preview_data = preview_data
    table.error = err
    table.save(update_fields=["preview_data", "error"])


def process_excel_file(dataset: Dataset):
    pd_excel = pd.ExcelFile(dataset.file.file.path)
    default_props = get_default_table_properties()
    with transaction.atomic():
        for sheet_name in pd_excel.sheet_names:
            table_data = {
                "dataset": dataset,
                "name": sheet_name,  # User can modify this later
                "original_name": sheet_name,  # This cannot be modified
                "created_by": dataset.file.created_by,
                "modified_by": dataset.file.modified_by,
                "preview_data": {},
                "has_errored": False,
                "error": None,
                "properties": default_props,
            }
            table = Table.objects.create(**table_data)
            preview_data, err = extract_preview_data_from_excel(
                pd_excel, table.original_name, table.properties
            )
            table.preview_data = preview_data
            table.error = err
            table.save()


def process_csv_file(dataset: Dataset):
    name = os.path.basename(dataset.file.file.name)
    table_data = {
        "dataset": dataset,
        "name": name,  # This can be modified later
        "original_name": name,  # This cannot be modified
        "created_by": dataset.file.created_by,
        "modified_by": dataset.file.modified_by,
    }
    Table.objects.create(**table_data)


def create_dataset_and_tables(file: File) -> Dataset:
    dataset_data = {
        "created_by": file.created_by,
        "modified_by": file.modified_by,
        "name": os.path.basename(file.file.name),
        "file": file,
    }
    dataset = Dataset.objects.create(**dataset_data)
    # Now process file and create associated table
    extension = get_file_extension(file.file.name)

    if extension.lower() == "xlsx":
        process_excel_file(dataset)
    elif extension.lower() == "csv":
        process_csv_file(dataset)
    else:
        # TODO: Handle gracefully, or should we? because serializer already validates extension
        raise Exception("Invalid file type")
    return dataset


def perform_hash_join(joined_table: Table) -> Snapshot:
    """
    Perform hash based join. Make sure there is only one equality clause.
    """
    join_obj = joined_table.joined_from
    assert join_obj is not None, f"Table(id: {joined_table.pk}) should have join object"
    assert len(join_obj.clauses) == 1
    assert join_obj.clauses[0]["operation"] == JOIN_CLAUSE_OPERATIONS.EQUAL

    clause = join_obj.clauses[0]
    source_table, target_table = join_obj.source_table, join_obj.target_table

    """
    After joining, some column names might overlap In such case we
    leave the overlapping source column key as it is and only
    modify keys for target, for which we will just append _<table_id>.
    """
    source_data = dict(
        columns=source_table.data_columns,
        rows=source_table.data_rows,
        stats=source_table.data_column_stats,
    )
    target_data = dict(
        columns=target_table.data_columns,
        rows=target_table.data_rows,
        stats=target_table.data_column_stats,
    )
    new_cols, new_rows, new_stats = perform_hash_join_(
        clause,
        source_data,
        target_data,
        join_type=join_obj.join_type,
        conflicting_col_suffix=str(target_table.id),
    )
    # Create a snapshot
    snapshot = Snapshot.objects.create(
        table=joined_table,
        version=1,
        data_rows=new_rows,
        data_columns=new_cols,
        column_stats=new_stats,
    )
    # Create preview data
    new_cols, new_rows, _ = perform_hash_join_(
        clause,
        join_obj.source_table.preview_data,
        join_obj.target_table.preview_data,
        join_type=join_obj.join_type,
        conflicting_col_suffix=str(join_obj.target_table.id),
    )
    joined_table.preview_data = {
        "columns": new_cols,
        "rows": new_rows,
    }
    joined_table.save()
    return snapshot


def perform_hash_join_(
    clause,
    source_data,
    target_data,
    join_type,
    conflicting_col_suffix="_1",
) -> Tuple[List, List, List]:
    source_col = clause["source_column"]
    target_col = clause["target_column"]
    # TODO: implement other joins
    assert join_type == Join.JoinType.INNER_JOIN, "Only inner join is supported"

    source_cols, source_rows, source_stats = (
        source_data["columns"],
        source_data["rows"],
        source_data.get("stats") or [],  # Stats may not be present for preview data
    )
    target_cols, target_rows, target_stats = (
        target_data["columns"],
        target_data["rows"],
        target_data.get("stats") or [],  # Stats may not be present for preview data
    )

    # First create index on target columns which has the following structure
    # { value: [row_index1, row_index2] }
    target_index: Dict[str, List[int]] = create_column_index(target_col, target_rows)

    # Next, we need to find appropriate target column key names. Because, the two
    # tables might have same keyed cols
    source_col_keys = set([x["key"] for x in source_cols])
    target_col_keys = set([x["key"] for x in target_cols])
    common_keys = source_col_keys.intersection(target_col_keys)

    # The idea is to append the target column key name with the append
    # parameter to maintain uniqueness of columns
    target_col_key_map = {
        key: key if key not in common_keys else f"{key}{conflicting_col_suffix}"
        for key in target_col_keys
    }

    updated_target_cols = [
        {**col, "key": target_col_key_map[col["key"]]} for col in target_cols
    ]
    new_columns = source_cols + updated_target_cols

    updated_target_stats = [
        {**stat, "key": target_col_key_map[stat["key"]]} for stat in target_stats
    ]
    new_stats = source_stats + updated_target_stats

    def merge(source_row, target_row):
        new_target_row = {
            target_col_key_map[k]: v
            for k, v in target_row.items()
            # Omit the original key from target row, later we'll have new key
            # for each row
            if k != "key"
        }
        return {**source_row, **new_target_row}

    # Now iterate over source rows and perform join
    joined_rows: list = []
    for row in source_rows:
        source_val = row[source_col]
        target_row_indices = target_index.get(source_val) or []
        for i, target_ind in enumerate(target_row_indices):
            joined_row = merge(row, target_rows[target_ind])
            joined_rows.append(
                {"key": str(i), **joined_row}  # Each row must have a key attribute
            )
    return new_columns, joined_rows, new_stats


def perform_naive_join(table: Table, join_obj: Join):
    assert table.joined_from == join_obj
    raise Exception("not implemented")


def create_column_index(target_col: str, rows: list) -> Dict[str, List[int]]:
    index: Dict[Any, List[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        value = row[target_col]
        if value is None:
            continue
        index[value].append(i)
    return index
