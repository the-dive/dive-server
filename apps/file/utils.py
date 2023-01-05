import os
import pandas as pd
from django.db import transaction

from apps.file.models import File
from apps.core.models import Dataset, Table
from apps.core.validators import get_default_table_properties
from utils.common import get_file_extension
from utils.extraction import extract_preview_data


def process_excel_file(dataset: Dataset):
    pd_excel = pd.ExcelFile(dataset.file.file.path)
    default_props = get_default_table_properties()
    with transaction.atomic():
        for sheet_name in pd_excel.sheet_names:
            preview_data, err = extract_preview_data(pd_excel, sheet_name, default_props)
            table_data = {
                "dataset": dataset,
                "name": sheet_name,  # User can modify this later
                "original_name": sheet_name,  # This cannot be modified
                "created_by": dataset.file.created_by,
                "modified_by": dataset.file.modified_by,
                "preview_data": preview_data or {},
                "has_errored": err is not None,
                "error": err or None,
            }
            Table.objects.create(**table_data)


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
