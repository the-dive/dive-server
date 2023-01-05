import pandas as pd

from apps.file.models import File
from apps.core.models import Table
from utils.extraction import extract_preview_data_from_excel


def apply_table_properties_and_extract_preview(table: Table):
    if table.dataset.file.file_type == File.Type.EXCEL:
        pd_excel = pd.ExcelFile(table.dataset.file.file.path)
        preview_data, err = extract_preview_data_from_excel(pd_excel, table.original_name, table.properties)
    else:
        raise Exception('Extraction not implemented for filetypes other than excel')
    table.preview_data = preview_data
    table.error = err
    table.save()
