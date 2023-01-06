import pandas as pd
import logging
from typing import Optional
from celery import shared_task

from apps.file.models import File
from apps.core.models import Table
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
        extract_data_from_excel(pd_excel, table.original_name, table.properties)
    else:
        raise Exception(f"Extraction for {table.source_type} not implemented")
