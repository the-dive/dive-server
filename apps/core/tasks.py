import pandas as pd
import logging
from typing import Optional
from celery import shared_task

from apps.file.models import File
from apps.core.models import Table, Snapshot, Action
from apps.core.types import ExtractedData
from apps.core.actions import parse_raw_action, BaseAction
from utils.extraction import extract_data_from_excel

logger = logging.getLogger(__name__)


@shared_task
def extract_table_data(table_id: int):
    table: Optional[Table] = Table.objects.filter(id=table_id).first()
    if table is None:
        logger.warning(f"No such table(id: {table_id}) exists to extract data")
        return

    if table.source_type == File.Type.EXCEL:
        pd_excel = pd.ExcelFile(table.dataset.file.file.path)
        extracted_data, err = extract_data_from_excel(
            pd_excel, table.original_name, table.properties, calculate_stats=True
        )
        if extracted_data is None:
            logger.warning(f"Error extracting data: {err}")
            return
        create_snapshot_from_extracted_data(table, extracted_data)
    else:
        raise Exception(f"Extraction for {table.source_type} not implemented")


def create_snapshot_from_extracted_data(table: Table, extracted_data: ExtractedData):
    return Snapshot.objects.create(
        table=table,
        version=1,
        data_rows=extracted_data["rows"],
        data_columns=extracted_data["columns"],
        column_stats=extracted_data["column_stats"],
    )


def get_composed_action_for_action_object(action_obj: Action) -> BaseAction:
    """
    Given an unapplied action object for a table, fetch all unapplied actions
    before it and create a composed action and return it.
    """
    # Fetch all actions which are not associated to snapshot
    action_objs_qs = Action.objects.filter(
        table=action_obj.table,
        order__lte=action_obj.order,
        snapshot__isnull=True,
    ).order_by('order')

    actions = [
        act
        for obj in action_objs_qs
        if (
            act := parse_raw_action(
                obj.action_name,
                obj.parameters,
                action_obj.table
            )) is not None
    ]
    ComposedAction = BaseAction.compose(actions)
    # NOTE: "ComposedAction" below: passing params and table leaves a hole that constituent actions can
    # be associated with one table while we can pass different table in
    # ComposedAction constructor
    return ComposedAction(params=[], table=action_obj.table)


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
