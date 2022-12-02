import os
import pandas as pd

from django.db import models
from django.dispatch import receiver

from apps.file.models import File
from apps.core.models import (
    Dataset,
    Table,
)


@receiver(models.signals.post_save, sender=File)
def create_dataset_and_table(sender, instance, created, **kwargs):
    """
    When file is created, create associated dataset and table
    """
    if instance:
        file_url = instance.file.path
        file_size_bytes = os.path.getsize(instance.file.path)
        file_name = os.path.basename(instance.file.name)
        dataset_data = {
            "file_url": file_url,
            "file_size_bytes": file_size_bytes,
            "created_by": instance.created_by,
            "modified_by": instance.modified_by,
            "name": file_name,
        }
        dataset = Dataset.objects.create(**dataset_data)
        # Now process file and create associated table
        extension = os.path.splitext(instance.file.name)[1].replace(".", "")
        if extension.lower() == "xlsx":
            sheetname = pd.ExcelFile(instance.file.path)
            sheets = [sheet for sheet in sheetname.sheet_names]
            for sheet in sheets:
                table_data = {
                    "dataset": dataset,
                    "name": sheet,
                    "created_by": instance.created_by,
                    "modified_by": instance.modified_by,
                }
                Table.objects.create(**table_data)
        elif extension.lower() == "csv":
            table_data = {
                "dataset": dataset,
                "name": os.path.basename(instance.file.name),
                "created_by": instance.created_by,
                "modified_by": instance.modified_by,
            }
            Table.objects.create(**table_data)
