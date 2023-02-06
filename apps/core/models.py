import copy
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

from dive.base_models import BaseModel, NamedModelMixin
from apps.file.models import File
from .validators import validate_table_properties, get_default_table_properties


class Dataset(BaseModel, NamedModelMixin):
    class DatasetStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        UPLOADED = "uploaded", _("Uploaded")
        EXTRACTED = "extracted", _("Extracted")

    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=50,
        choices=DatasetStatus.choices,
        default=DatasetStatus.PENDING,
    )
    has_errored = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    extra_data = models.JSONField(default=dict)


class Table(BaseModel, NamedModelMixin):
    class TableStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        EXTRACTED = "extracted", _("Extracted")

    # This is the original name of the table(sheet name in case of excel or the file name in case of csvs)
    original_name = models.CharField(max_length=255)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=TableStatus.choices,
        default=TableStatus.PENDING,
    )
    properties = models.JSONField(
        default=get_default_table_properties, validators=[validate_table_properties]
    )
    preview_data = models.JSONField(blank=True, null=True)
    is_added_to_workspace = models.BooleanField(default=False)
    extra_data = models.JSONField(default=dict)
    has_errored = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)
    cloned_from = models.ForeignKey(
        "Table", on_delete=models.SET_NULL, null=True, blank=True
    )

    def clone(self):
        cloned_table = copy.deepcopy(self)
        cloned_table.pk = None
        cloned_table.cloned_from = self
        cloned_table.name = f"Copy of {self.name}"
        cloned_table.save()
        return cloned_table

    @property
    def last_snapshot(self) -> Optional["Snapshot"]:
        return Snapshot.objects.filter(table=self).order_by("-created_at").first()

    @property
    def data_rows(self):
        if self.last_snapshot is None:
            return []
        return self.last_snapshot.data_rows

    @property
    def data_columns(self):
        if self.last_snapshot is None:
            return []
        return self.last_snapshot.data_columns

    @property
    def data_column_stats(self):
        if self.last_snapshot is None:
            return []
        return self.last_snapshot.column_stats

    @cached_property
    def source_type(self):
        return self.dataset.file.file_type


class Snapshot(BaseModel):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    version = models.PositiveIntegerField()
    # TODO: validation and types for json fields
    data_rows = models.JSONField()
    data_columns = models.JSONField()
    column_stats = models.JSONField()

    def __str__(self):
        return f"{self.table.original_name} - {self.version}"


class Action(BaseModel, NamedModelMixin):
    """
    Every action is associated with a table(and possibly a column)
    Try to model these as functions. Examples:
    1. Casting Column: cast(column, target_type)
    2. Deleting a Column: delete(column)
    """

    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    snapshot = models.ForeignKey(Snapshot, null=True, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField()
    # TODO: JSON validations for parameters
    parameters = models.JSONField(default=list)

    class Meta:
        unique_together = ("table", "order")

    def save(self, *args, **kwargs):
        if self.pk:
            raise Exception("Cannot update action after creation")
        super().save(*args, **kwargs)
