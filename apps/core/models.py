from django.db import models
from django.utils.translation import gettext_lazy as _

from dive.base_models import BaseModel, NamedModelMixin
from apps.file.models import File
from utils.common import ColumnTypes
from .validators import validate_table_properties


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

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=TableStatus.choices,
        default=TableStatus.PENDING,
    )
    properties = models.JSONField(default=dict, validators=[validate_table_properties])
    preview_data = models.JSONField(blank=True, null=True)
    is_added_to_workspace = models.BooleanField(default=False)
    extra_data = models.JSONField(default=dict)
    has_errored = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)


class Column(BaseModel, NamedModelMixin):
    class StatsStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")
        ERRORED = "errored", _("Errored")

    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=50,
        choices=ColumnTypes.choices,
    )
    properties = models.JSONField(default=dict)
    stats = models.JSONField(default=dict)
    stats_calculation_status = models.CharField(
        max_length=20,
        choices=StatsStatus.choices,
        default=StatsStatus.PENDING,
    )
    extra_data = models.JSONField(default=dict)


class Action(BaseModel, NamedModelMixin):
    class ActionType(models.TextChoices):
        COLUMN_WISE = "column-wise", _("Column Wise")
        TABLE_WISE = "table-wise", _("Table Wise")

    table = models.ForeignKey(Table, null=True, on_delete=models.SET_NULL)
    column = models.ForeignKey(Column, null=True, on_delete=models.SET_NULL)
    snapshot_version = models.CharField(max_length=20)
    type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
    )
    order = models.PositiveIntegerField()
    # TODO: JSON validations for parameters
    parameters = models.JSONField(default=dict)
    extra_data = models.JSONField(default=dict)

    class Meta:
        unique_together = ("table", "snapshot_version", "order")
