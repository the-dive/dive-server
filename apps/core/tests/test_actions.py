import pytest
from typing import cast

from dive.base_test import BaseTestWithDataFrameAndExcel
from apps.core.actions import CastColumnAction, get_action_class, parse_raw_action
from apps.core.tasks import extract_table_data
from apps.core.models import Snapshot
from utils.common import ColumnTypes

STRING_STAT_KEYS = ["total_count", "na_count", "unique_count", "max_length", "min_length"]
NUMERIC_STAT_KEYS = ["min", "max", "median", "std_deviation", "total_count", "na_count"]


def test_get_action_class_invalid_name():
    """
    Tests if invalid or unregistered action name gives None
    """
    invalid_names = ["random action", "", None]
    for name in invalid_names:
        assert get_action_class(name) is None


@pytest.mark.django_db
class TestCastColumnAction(BaseTestWithDataFrameAndExcel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_name = "cast_column"
        self.action_class = CastColumnAction

    def setUp(self):
        super().setUp()
        # Sample row: {"0": 1, "1": "Sam", "2": 2000, "key": "0"}
        self.table = self.dataset.table_set.first()
        # Extract table data to create snapshot
        extract_table_data(self.table.id)

    def test_get_action_class(self):
        assert get_action_class(self.action_name) == self.action_class

    def test_parse_action_with_inexistent_column(self):
        inexistent_column = "random_col"
        params = [inexistent_column, "string"]
        action = parse_raw_action(self.action_name, params, self.table)
        assert action is not None
        assert action.is_valid is False
        assert action.error, "Error should be present"

    def test_parse_action(self):
        # Sample row: {"0": 1, "1": "Sam", "2": 2000, "key": "0"}
        params = ["0", "string"]
        action = parse_raw_action(self.action_name, params, self.table)
        assert action is not None
        assert action.is_valid is True
        assert not action.error, "Error should not be present"

    def test_apply_action_to_row(self):
        params = ["0", "string"]
        action = cast(CastColumnAction, parse_raw_action(self.action_name, params, self.table))
        assert action is not None
        assert action.is_valid is True

        # Set up actions
        col_key = "0"
        # row 0 of the table
        row = self.table.last_snapshot.data_rows[0]
        assert isinstance(row[col_key], int)
        new_row = action.apply_row(row)
        assert isinstance(new_row[col_key], str)

    def test_apply_action_to_table(self):
        params = ["0", "string"]
        action = cast(CastColumnAction, parse_raw_action(self.action_name, params, self.table))
        assert action is not None
        assert action.is_valid is True

        # Set up actions
        col_key = "0"

        # Test original column data, row data and stats
        snapshot = self.table.last_snapshot
        original_columns = snapshot.data_columns

        # Test stats
        original_stats = snapshot.column_stats
        col_stats = next(x for x in original_stats if x["key"] == col_key)
        for stat_key in NUMERIC_STAT_KEYS:
            assert stat_key in col_stats, f"Integer column should have {stat_key} in stats"

        # First assert column type has integer
        for col in original_columns:
            if col["key"] == col_key:
                assert col["type"] == ColumnTypes.INTEGER

        # Assert all row have int for col_key
        for row in self.table.last_snapshot.data_rows:
            assert isinstance(row[col_key], int)

        # Apply action to table
        action.apply_table(self.table)

        assert Snapshot.objects.filter(table=self.table, version=2).exists(),\
            "A snapshot with version 2 should have been created"

        new_stats = self.table.last_snapshot.column_stats
        col_stats_new = next(x for x in new_stats if x["key"] == col_key)
        for stat_key in STRING_STAT_KEYS:
            assert stat_key in col_stats_new, f"String column should have {stat_key} in stats"

        # After application, assert all row have str for col_key
        for row in self.table.last_snapshot.data_rows:
            assert isinstance(row[col_key], str)

        # Also check if column type for col_key is changed to string
        new_columns = self.table.last_snapshot.data_columns
        for col in new_columns:
            if col["key"] == col_key:
                assert col["type"] == ColumnTypes.STRING
