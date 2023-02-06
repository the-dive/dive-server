from dive.base_test import BaseTestWithDataFrameAndExcel
from apps.core.models import Snapshot
from apps.core.tasks import extract_table_data


class TestTasks(BaseTestWithDataFrameAndExcel):
    def test_extract_table_data(self):
        table = self.dataset.table_set.first()
        assert table is not None
        assert not Snapshot.objects.filter(table=table).exists()
        extract_table_data(table.id)
        snapshot = Snapshot.objects.filter(table=table).first()
        assert snapshot is not None
        assert snapshot.version == 1
