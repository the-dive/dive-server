import os
import pandas as pd
from django.db import transaction

from apps.file.models import File
from apps.core.models import Dataset, Table
from utils.common import get_file_extension
from utils.extraction import extract_preview_data


# TODO: add other attributes and add typings
DEFAULT_TABLE_PROPERTIES = {
    "header": 1,
}


def process_excel_file(dataset: Dataset):
    pd_excel = pd.ExcelFile(dataset.file.file.path)
    sheets = [sheet for sheet in pd_excel.sheet_names]
    with transaction.atomic():
        for sheet in sheets:
            preview_data, err = extract_preview_data(pd_excel, sheet)
            table_data = {
                "dataset": dataset,
                "name": sheet,
                "created_by": dataset.file.created_by,
                "modified_by": dataset.file.modified_by,
                "preview_data": preview_data or {},
                "has_errored": err is not None,
                "error": err or None,
            }
            Table.objects.create(**table_data)


def process_csv_file(dataset: Dataset):
    table_data = {
        "dataset": dataset,
        "name": os.path.basename(dataset.file.file.name),
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
