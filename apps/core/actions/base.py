from typing import Optional, Type, Dict, List, Tuple, Any
from functools import reduce

from apps.core.models import Table, Snapshot
from apps.core.types import Validation

from utils.extraction import calculate_single_column_stats
from utils.parsing import parse_type


__ACTIONS: Dict[str, Type] = {}


def get_action_class(name: str) -> Optional[Type]:
    return __ACTIONS.get(name)


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


def get_all_action_names() -> List[str]:
    return list(__ACTIONS.keys())


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

    @classmethod
    def compose(cls, actions: List["BaseAction"]) -> Type["BaseAction"]:
        class ComposedAction(BaseAction):
            def validate(self, params, table):
                """
                Iterate over all actions and if any of them is not valid,
                return invalid. Else return valid
                """
                for act in actions:
                    if not act.is_valid:
                        return False, act.error
                return True, None

            def apply_row(self, row: dict) -> dict[str, Any]:
                return reduce(
                    lambda new_row, action: action.apply_row(new_row),
                    actions,
                    row,
                )

            def apply_columns(self, columns):
                new_cols, affected_cols = columns, []
                for act in actions:
                    new_cols, affected_cols_ = act.apply_columns(new_cols)
                    affected_cols = list(set([*affected_cols, *affected_cols_]))
                return new_cols, affected_cols

        return ComposedAction

    def base_validate(self, params: List[str], _: Table) -> Validation:
        if len(params) != len(self.PARAM_TYPES):
            return False, "Invalid number of parameters."

        for i, (param, typ) in enumerate(zip(params, self.PARAM_TYPES)):
            if parse_type(typ, param) is None:
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

    def apply_table(self):
        snapshot, new_rows, new_columns, column_stats = self.run_action()
        # Create new snapshot
        snapshot.id = None
        snapshot.version = snapshot.version + 1
        snapshot.data_rows = new_rows
        snapshot.data_columns = new_columns
        snapshot.column_stats = column_stats
        snapshot.save()

    def run_action(self) -> Tuple[Snapshot, List[dict], List[dict], List[dict]]:
        """
        Returns a tuple containing:
        (
            snapshot on which the action ran,
            new_rows,
            new_columns,
            column_stats
        )
        """
        if not self.is_valid:
            raise Exception("Calling run_action() when is_valid is False")
        snapshot: Optional[Snapshot] = self.table.last_snapshot
        if snapshot is None:
            raise Exception("Calling run_action() when table has no snapshot")

        new_rows = [self.apply_row(x) for x in snapshot.data_rows or []]

        new_columns, affected_column_ids = self.apply_columns(snapshot.data_columns)

        # Only calculate stats for the affected columns
        column_stats = [
            next(
                col_stat
                for col_stat in snapshot.column_stats
                if col_stat["key"] == col["key"]
            )
            if col["key"] not in affected_column_ids
            else {
                "type": col["type"],
                "key": col["key"],
                "label": col["label"],
                **calculate_single_column_stats(
                    [x[col["key"]] for x in new_rows], col["type"]
                ),
            }
            for col in new_columns
        ]
        return snapshot, new_rows, new_columns, column_stats

    def apply_row(self, row: dict):
        """Apply the action to single table row. Results in new set of table row."""
        raise MethodNotImplemented

    def apply_columns(self, cols: List[dict]) -> Tuple[List[dict], List[str]]:
        """Get new columns and affected column keys as tuples: (new_cols, affected_col_ids)"""
        raise MethodNotImplemented
