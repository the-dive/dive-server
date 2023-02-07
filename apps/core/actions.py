from typing import Optional, Type, Dict

from apps.core.models import Table, Snapshot
from apps.core.types import Validation

from utils.extraction import calculate_single_column_stats
from utils.parsing import parse
from utils.common import ColumnTypes


__ACTIONS: Dict[str, Type] = {}


def register_action(cls):
    """
    Takes in a class with NAME attribute and checks if it exists in __ACTIONS.
    If it does, raises exception, else registers the action.
    """
    global __ACTIONS
    if not hasattr(cls, "NAME") or not cls.NAME:
        raise Exception(
            "Empty action name. Please provide valid name as NAME class attribute."
        )
    name = cls.NAME
    if name in __ACTIONS:
        raise Exception(f"Action {name} is already registered.")
    __ACTIONS[name] = cls
    return cls


class MethodNotImplemented(Exception):
    pass


class BaseAction:
    """
    This is the base class for implementing actions. It requires two class attributes:
    1. NAME: str, unique name for the action.
    2. PARAM_TYPES: list, types of params. Eg. [int, str] or [str, float, int, str]

    Its major methods are:
    1. validate(params_list, table): Basic validation is already implemented
    2. apply_table(table): Apply the action to table and return new snapshot
    2. apply_row(row_dict): Apply the action to row dict and return new dict
    """

    NAME = ""
    PARAM_TYPES = []

    def __init__(self, params, table: Table):
        self.is_valid, self.error = self.validate(params, table)
        self.params = params
        self.table = table

    def base_validate(self, params: list, _: Table) -> Validation:
        if len(params) != len(self.PARAM_TYPES):
            return False, "Invalid number of parameters."

        for i, (param, typ) in enumerate(zip(params, self.PARAM_TYPES)):
            if not isinstance(param, typ):
                return (
                    False,
                    f"Invalid type {type(param)} for parameter {i}. Expected {typ}.",
                )

        return True, ""

    def validate_column(self, params: list, table: Table) -> Validation:
        if len(params) == 0:
            return True, None

        last_snapshot: Optional[Snapshot] = table.last_snapshot
        if last_snapshot is None:
            return False, "No snapshot for table"
        col_id, *_ = params
        column_ids = [col["key"] for col in last_snapshot.data_columns or []]
        if col_id is not None and col_id not in column_ids:
            return False, "Invalid column id"
        return True, None

    def validate(self, params: list, table: Table) -> Validation:
        """
        Validate the params along with table. The first element of params list is
        the column name or None which indicates action is applied to all columns.
        """
        is_valid, err = self.base_validate(params, table)
        if not is_valid:
            return is_valid, err

        return self.validate_column(params, table)

    def apply_table(self, table: Table):
        """Apply the action to whole table. Results in new set of table rows/columns."""
        raise MethodNotImplemented

    def apply_row(self, row: dict):
        """Apply the action to single table row. Results in new set of table row."""
        raise MethodNotImplemented


def get_action_class(name: str) -> Optional[Type]:
    return __ACTIONS.get(name)


def parse_raw_action(raw_action: list, table: Table) -> Optional[BaseAction]:
    if not raw_action:
        return None
    action_name, *params = raw_action
    Action = get_action_class(action_name)
    return Action and Action(params, table)


@register_action
class CastColumnAction(BaseAction):
    NAME = "cast_column"
    PARAM_TYPES = [str, str]  # [col_id, type]

    def validate(self, params: list, table: Table) -> Validation:
        is_valid, err = super().validate(params, table)
        if not is_valid:
            return is_valid, err
        _, target_type = params
        if target_type not in [
            ColumnTypes.INTEGER,
            ColumnTypes.STRING,
        ]:  # TODO: add other types
            return False, f"Invalid target type '{target_type}'"
        return True, None

    def apply_table(self, table: Table):
        if not self.is_valid:
            raise Exception("Calling apply_table() when is_valid is False")
        snapshot: Optional[Snapshot] = table.last_snapshot
        if snapshot is None:
            return
        new_rows = [self.apply_row(x) for x in snapshot.data_rows or []]

        col_key, target_type = self.params
        # Update column type: update type if col["key"] equals col_key
        new_columns = [
            col if col["key"] != col_key else {**col, "type": target_type}
            for col in snapshot.data_columns
        ]

        # Create new snapshot
        snapshot.id = None
        snapshot.version = snapshot.version + 1
        snapshot.data_rows = new_rows
        snapshot.data_columns = new_columns
        snapshot.column_stats = [
            col_stats
            if col_stats["key"] != col_key
            else {
                "type": target_type,
                "key": col_key,
                "label": col_stats["label"],
                **calculate_single_column_stats([x[col_key] for x in new_rows], target_type)
            }
            for col_stats in snapshot.column_stats
        ]
        snapshot.save()

    def apply_row(self, row: dict):
        if not self.is_valid:
            raise Exception("Calling apply_row() when is_valid is False")
        col_id, target_type = self.params  # parameters validation already happens in base class
        return {**row, col_id: parse(row[col_id], target_type)}
