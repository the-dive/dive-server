import os
import pandas as pd

from apps.core.models import Dataset, Table


def create_dataset_table(file):
    dataset_data = {
        "created_by": file.created_by,
        "modified_by": file.modified_by,
        "name": os.path.basename(file.file.name),
        "file": file,
    }
    dataset = Dataset.objects.create(**dataset_data)
    # Now process file and create associated table
    extension = os.path.splitext(file.file.name)[1].replace(".", "")
    if extension.lower() == "xlsx":
        sheetname = pd.ExcelFile(file.file.path)
        sheets = [sheet for sheet in sheetname.sheet_names]
        for sheet in sheets:
            table_data = {
                "dataset": dataset,
                "name": sheet,
                "created_by": file.created_by,
                "modified_by": file.modified_by,
            }
            Table.objects.create(**table_data)
    elif extension.lower() == "csv":
        table_data = {
            "dataset": dataset,
            "name": os.path.basename(file.file.name),
            "created_by": file.created_by,
            "modified_by": file.modified_by,
        }
        Table.objects.create(**table_data)
