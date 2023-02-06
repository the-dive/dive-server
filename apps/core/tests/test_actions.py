import pytest

from dive.base_test import BaseTestWithDataFrameAndExcel
from apps.core.actions import CastColumn, get_action_class, parse_raw_action
from apps.core.tasks import extract_table_data
from utils.common import ColumnTypes


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
        self.action_class = CastColumn

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
        raw_action = ["cast_column", inexistent_column, "string"]
        action = parse_raw_action(raw_action, self.table)
        assert action is not None
        assert action.is_valid is False
        assert action.error, "Error should be present"

    def test_parse_action(self):
        # Sample row: {"0": 1, "1": "Sam", "2": 2000, "key": "0"}
        raw_action = ["cast_column", "0", "string"]
        action = parse_raw_action(raw_action, self.table)
        assert action is not None
        assert action.is_valid is True
        assert not action.error, "Error should not be present"

    def test_apply_action_to_row(self):
        raw_action = ["cast_column", "0", "string"]
        action = parse_raw_action(raw_action, self.table)
        assert action is not None
        assert action.is_valid is True

        # Set up actions
        col_key = "0"
        target_type = "string"
        raw_action = ["cast_column", col_key, target_type]

        # row 0 of the table
        row = self.table.last_snapshot.data_rows[0]
        assert isinstance(row[col_key], int)
        new_row = action.apply_row(row)
        assert isinstance(new_row[col_key], str)

    def test_apply_action_to_table(self):
        raw_action = ["cast_column", "0", "string"]
        action = parse_raw_action(raw_action, self.table)
        assert action is not None
        assert action.is_valid is True

        # Set up actions
        col_key = "0"
        target_type = "string"
        raw_action = ["cast_column", col_key, target_type]

        # Test original column data and row data
        original_columns = self.table.last_snapshot.data_columns
        # First assert column type has integer
        for col in original_columns:
            if col["key"] == col_key:
                assert col["type"] == ColumnTypes.INTEGER

        # Assert all row have int for col_key
        for row in self.table.last_snapshot.data_rows:
            assert isinstance(row[col_key], int)

        # Apply action to table
        action.apply_table(self.table)

        # After application, assert all row have str for col_key
        for row in self.table.last_snapshot.data_rows:
            assert isinstance(row[col_key], str)

        # Also check if column type for col_key is changed to string
        new_columns = self.table.last_snapshot.data_columns
        for col in new_columns:
            if col["key"] == col_key:
                assert col["type"] == ColumnTypes.STRING
