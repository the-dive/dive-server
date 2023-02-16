import copy
from typing import Optional

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

from dive.base_models import BaseModel, NamedModelMixin
from apps.file.models import File
from .validators import (
    validate_table_properties,
    get_default_table_properties,
    validate_join_clauses,
)


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
        default=get_default_table_properties,
        validators=[validate_table_properties],
    )
    preview_data = models.JSONField(blank=True, null=True)
    is_added_to_workspace = models.BooleanField(default=False)
    extra_data = models.JSONField(default=dict)
    has_errored = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)
    cloned_from = models.OneToOneField(
        "Table",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    joined_from = models.OneToOneField(
        "Join",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def clone(self):
        cloned_table = copy.deepcopy(self)
        cloned_table.pk = None
        cloned_table.cloned_from = self
        cloned_table.name = f"Copy of {self.name}"
        cloned_table.save()
        return cloned_table

    @property
    def last_unapplied_action(self) -> Optional["Action"]:
        return (
            self.action_set.filter(snapshot__isnull=True)
            .order_by("-created_at")
            .first()
        )

    @property
    def last_snapshot(self) -> Optional["Snapshot"]:
        return self.snapshot_set.order_by("-created_at").first()

    @property
    def data_rows(self):
        """
        Ideally we would have snapshot for each action. However, we don't do
        that. so, the rows for table at any moment is the application of all
        the actions since the last snapshot.
        """
        # Importing here because this introduces circular import, which at the moment
        # cannot be fixed properly
        from apps.core.actions.utils import get_composed_action_for_action_object

        if self.last_snapshot is None:
            return []
        # TODO: paginate
        if self.last_unapplied_action is not None:
            # If there are any unapplied actions, fetch them, merge them into a
            # single action and apply to the last snapshot row
            composed_action = get_composed_action_for_action_object(
                self.last_unapplied_action
            )
            return [
                composed_action.apply_row(row) for row in self.last_snapshot.data_rows
            ]
        else:
            return self.last_snapshot.data_rows

    @property
    def data_columns(self):
        if self.last_snapshot is None:
            return []
        if self.last_unapplied_action is not None:
            # Actually table_column_stats in action object contains all info about
            # the updated columns, fetch data from there and return
            stats = self.last_unapplied_action.table_column_stats
            return [
                {"key": stat["key"], "label": stat["label"], "type": stat["type"]}
                for stat in stats
            ]
        return self.last_snapshot.data_columns

    @property
    def data_column_stats(self):
        """If there is unapplied action, return column stats from the action
        else return stats from the snapshot
        """
        if self.last_snapshot is None:
            return []
        if self.last_unapplied_action is not None:
            return self.last_unapplied_action.table_column_stats
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
    column_stats = models.JSONField(default=list)

    def __str__(self):
        return f"{self.table.original_name} - {self.version}"


class Action(BaseModel, NamedModelMixin):
    """
    Every action is associated with a table(and possibly a column)
    Try to model these as functions. Examples:
    1. Casting Column: cast(column, target_type)
    2. Deleting a Column: delete(column)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The following fields cannot be updated after created. So,
        # they are tracked in private attributes. See save() method
        # for their usage.
        self.__action_name = self.action_name
        self.__order = self.order
        self.__parameters = self.parameters
        self.__table = self.table

    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    """
    IMPORTANT!!
    A snapshot in an action means that the action has been applied to some
    previous snapshot(table.last_snapshot) and a new snapshot has been created.
    The snapshot field defined below is that new snapshot.

    So, when there are unapplied actions(actions that are not associated with any
    snapshot, we aggregate them, compose them and apply to the last_snapshot of the
    table and create a new one.
    """
    snapshot = models.ForeignKey(Snapshot, null=True, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField()
    action_name = models.CharField(max_length=100)
    parameters = ArrayField(models.CharField(max_length=200))
    """
    IMPORTANT!!
    Our idea is to not create a new snapshot for every action, that would take
    up much space. We can serve the rows applied with actions on the fly when
    API requests. However, stats change after each action and calculating stats
    on the fly for each request is not feasible(because stats operate on whole
    transformed data while actions can be applied to only the paginated rows on
    the fly). Thus, we need to associate each action with the table stats.

    However, there's a catch with this approach althouth this works fine for
    single action on a snapshot. For multiple actions, how do we calculate the
    stats for the last action? Because, for the first action, we have a
    snapshot on which we apply the action and calculate stats. But for
    subsequent actions, we won't have snapshots due to which we won't have data
    to apply that action on and calculate stats. To mitigate this, we are going
    to chain all the actions from an snapshot to the latest action and apply
    the chain of actions to the snapshot data and then calculate stats. This
    process repeats after we create new snapshot.

    A natural question to ask here is that why not we calculate snapshot for
    each action which will prevent running actions repeatedly every time new
    action is added. Well I(@bewakes) think, we are more concerned about the
    space/storage requirements than by ocassional calculations. Of course, this
    is an open question and the answer might change based on the usage in
    future. But for now I think this should be good enough.
    """
    table_column_stats = models.JSONField(default=list)

    class Meta:
        unique_together = ("table", "order")

    def save(self, *args, **kwargs):
        if (
            self.__table != self.table
            or self.__order != self.order
            or self.__action_name != self.action_name
            or self.__parameters != self.parameters
        ):
            raise Exception(
                "Cannot update fields table, order, action_name and parameters after creation"
            )
        super().save(*args, **kwargs)


class Join(BaseModel):
    class JoinType(models.TextChoices):
        INNER_JOIN = "inner_join", _("Inner Join")
        OUTER_JOIN = "outer_join", _("Outer Join")
        LEFT_JOIN = "left_join", _("Left Join")
        RIGHT_JOIN = "right_join", _("Right Join")

    source_table = models.ForeignKey(
        Table, on_delete=models.CASCADE, related_name="join_sources"
    )
    target_table = models.ForeignKey(
        Table, on_delete=models.CASCADE, related_name="join_targets"
    )
    join_type = models.CharField(max_length=20, choices=JoinType.choices)
    clauses = models.JSONField(default=list, validators=[validate_join_clauses])

    def __str__(self):
        return f"{self.source_table}::{self.join_type}::{self.target_table}"
