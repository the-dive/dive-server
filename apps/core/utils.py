import pandas as pd

from apps.core.models import Table
from utils.extraction import extract_preview_data


def apply_table_properties(table: Table):
    pd_excel = pd.ExcelFile(table.dataset.file.file.path)
    preview_data, err = extract_preview_data(pd_excel, table.original_name, table.properties)
    table.preview_data = preview_data
    table.error = err
    table.save()
