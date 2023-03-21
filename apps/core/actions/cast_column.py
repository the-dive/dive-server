from typing import List, Tuple

from .base import register_action, BaseAction
from apps.core.types import Validation
from apps.core.models import Table
from utils.common import ColumnTypes
from utils.parsing import parse


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
            ColumnTypes.NUMBER,
            ColumnTypes.INTEGER,
            ColumnTypes.STRING,
            ColumnTypes.DATE,
            ColumnTypes.DATETIME,
        ]:  # TODO: add other types
            return False, f"Invalid target type '{target_type}'"
        return True, None

    def apply_columns(self, columns: List[dict]) -> Tuple[List[dict], List[str]]:
        col_key, target_type = self.params
        affected_col_keys = [col_key]
        # Update column type: update type if col["key"] equals col_key
        new_cols = [
            col if col["key"] != col_key else {**col, "type": target_type}
            for col in columns
        ]
        return new_cols, affected_col_keys

    def apply_row(self, row: dict):
        if not self.is_valid:
            raise Exception("Calling apply_row() when is_valid is False")
        (
            col_id,
            target_type,
        ) = self.params  # parameters validation already happens in base class
        return {**row, col_id: parse(row[col_id], target_type)}
