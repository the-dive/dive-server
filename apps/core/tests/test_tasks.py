from unittest import mock

from dive.base_test import BaseTestWithDataFrameAndExcel
from apps.core.models import Snapshot, Action
from apps.core.tasks import (
    extract_table_data,
    calculate_column_stats_for_action,
    create_snapshot_for_table,
)


class TestTasks(BaseTestWithDataFrameAndExcel):
    def test_extract_table_data(self):
        table = self.dataset.table_set.first()
        assert table is not None
        assert not Snapshot.objects.filter(table=table).exists()
        extract_table_data(table.id)
        snapshot = Snapshot.objects.filter(table=table).first()
        assert snapshot is not None
        assert snapshot.version == 1

    @mock.patch("apps.core.tasks.get_composed_action_for_action_object")
    def test_calculate_column_stats_for_action_inexistent_action(
        self, composed_action_func
    ):
        inexistent_action_id = 11
        calculate_column_stats_for_action(inexistent_action_id)
        composed_action_func.assert_not_called()

    def test_calculate_column_stats_for_action(self):
        table = self.dataset.table_set.first()
        # Create snapshot first
        create_snapshot_for_table(table)

        col_key = "0"
        action = Action.objects.create(
            table=table,
            action_name="cast_column",
            parameters=[col_key, "string"],
            order=1,
        )
        assert not action.table_column_stats
        calculate_column_stats_for_action(action.id)
        action = Action.objects.get(id=action.id)
        assert action.table_column_stats
        column = next(x for x in action.table_column_stats if x["key"] == col_key)
        assert column["type"] == "string", "Column type should be changed to string"
