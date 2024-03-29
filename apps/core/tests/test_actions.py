import pytest
from typing import cast

from dive.base_test import BaseTestWithDataFrameAndExcel
from apps.core.actions.base import get_action_class
from apps.core.actions.utils import parse_raw_action
from apps.core.actions.cast_column import CastColumnAction
from apps.core.tasks import extract_table_data, calculate_column_stats_for_action
from apps.core.models import Snapshot, Action
from utils.common import ColumnTypes

STRING_STAT_KEYS = [
    "total_count",
    "na_count",
    "unique_count",
    "max_length",
    "min_length",
]
NUMERIC_STAT_KEYS = [
    "total_count",
    "na_count",
    "min",
    "max",
    "median",
    "std_deviation",
]


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
        action = cast(
            CastColumnAction, parse_raw_action(self.action_name, params, self.table)
        )
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
        action = cast(
            CastColumnAction, parse_raw_action(self.action_name, params, self.table)
        )
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
            assert (
                stat_key in col_stats
            ), f"Integer column should have {stat_key} in stats"

        # First assert column type has integer
        for col in original_columns:
            if col["key"] == col_key:
                assert col["type"] == ColumnTypes.INTEGER

        # Assert all row have int for col_key
        for row in self.table.last_snapshot.data_rows:
            assert isinstance(row[col_key], int)

        # Apply action to table
        action.apply_table()

        assert Snapshot.objects.filter(
            table=self.table, version=2
        ).exists(), "A snapshot with version 2 should have been created"

        new_stats = self.table.last_snapshot.column_stats
        col_stats_new = next(x for x in new_stats if x["key"] == col_key)
        for stat_key in STRING_STAT_KEYS:
            assert (
                stat_key in col_stats_new
            ), f"String column should have {stat_key} in stats"

        # After application, assert all row have str for col_key
        for row in self.table.last_snapshot.data_rows:
            assert isinstance(row[col_key], str)

        # Also check if column type for col_key is changed to string
        new_columns = self.table.last_snapshot.data_columns
        for col in new_columns:
            if col["key"] == col_key:
                assert col["type"] == ColumnTypes.STRING

    def test_action_composition(self):
        # TODO: To be implemented by @bewakes, will do after other actions are
        # added. Currently we only have a single action
        pass

    def test_action_rows_after_an_action(self):
        """Test if rows are different from the snapshot rows after an action is
        issued which is not yet applied"""
        colkey = "0"
        params = [colkey, "string"]
        action_name = "cast_column"
        first_row_before_action = {**self.table.data_rows[0]}
        action_object = Action.objects.create(
            table=self.table,
            action_name=action_name,
            parameters=params,
            order=1,
        )
        # Test for column stats before and after action
        assert action_object.table_column_stats == []
        calculate_column_stats_for_action(action_object.id)
        action_object = Action.objects.get(pk=action_object.id)
        assert action_object.table_column_stats != []

        # Test for column actions for table
        assert self.table.data_column_stats == action_object.table_column_stats

        first_row_after_action = self.table.data_rows[0]
        assert isinstance(
            first_row_before_action[colkey], int
        ), "Before action, col is int"
        assert isinstance(
            first_row_after_action[colkey], str
        ), "After action, col is string"

    def test_cast_row_to_number(self):
        data = [
            {"name": "Dive", "age": "1", "bmi": "13.5"},
            {"name": "Deep", "age": None, "bmi": "18.0"},
            {"name": "DEEPL", "age": "3", "bmi": "eighteen"},
        ]
        age_casted_expected = [
            {"name": "Dive", "age": 1, "bmi": "13.5"},
            {"name": "Deep", "age": None, "bmi": "18.0"},
            {"name": "DEEPL", "age": 3, "bmi": "eighteen"},
        ]
        bmi_casted_expected = [
            {"name": "Dive", "age": "1", "bmi": 13.5},
            {"name": "Deep", "age": None, "bmi": 18.0},
            {"name": "DEEPL", "age": "3", "bmi": None},
        ]
        # Test cast age
        colkey = "age"
        params = [colkey, "number"]
        action = CastColumnAction(params, self.table)
        # Set is_valid true because the constructor requires table and params
        # to be consistent but we don't care about that for testing apply_row
        action.is_valid = True

        age_casted = [action.apply_row(row) for row in data]
        assert age_casted == age_casted_expected

        # Test cast bmi
        colkey = "bmi"
        params = [colkey, "number"]
        action = CastColumnAction(params, self.table)
        # Set is_valid true because the constructor requires table and params
        # to be consistent but we don't care about that for testing apply_row
        action.is_valid = True

        bmi_casted = [action.apply_row(row) for row in data]
        assert bmi_casted == bmi_casted_expected

    def test_cast_string_to_number_field(self):
        """Try to cast non numeric string to integer"""
        data = [
            {"name": "Dive", "age": "1", "bmi": "13.5"},
            {"name": "Deep", "age": None, "bmi": "18.0"},
            {"name": "DEEPL", "age": "3", "bmi": "eighteen"},
        ]
        name_casted_expected = [
            {"name": None, "age": "1", "bmi": "13.5"},
            {"name": None, "age": None, "bmi": "18.0"},
            {"name": None, "age": "3", "bmi": "eighteen"},
        ]
        # Test cast name
        colkey = "name"
        params = [colkey, "number"]
        action = CastColumnAction(params, self.table)
        # Set is_valid true because the constructor requires table and params
        # to be consistent but we don't care about that for testing apply_row
        action.is_valid = True

        name_casted = [action.apply_row(row) for row in data]
        assert name_casted == name_casted_expected
