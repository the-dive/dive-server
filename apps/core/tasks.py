import pandas as pd
import logging
from typing import Optional
from celery import shared_task

from apps.file.models import File
from apps.core.models import Table, Snapshot
from apps.core.types import ExtractedData
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
        create_snapshot_and_calculate_stats(table, extracted_data)
    else:
        raise Exception(f"Extraction for {table.source_type} not implemented")


def create_snapshot_and_calculate_stats(table: Table, extracted_data: ExtractedData):
    snapshot = Snapshot.objects.create(
        table=table,
        version=1,
        data_rows=extracted_data["rows"],
        data_columns=extracted_data["columns"],
    )

    # Calculate column stats
