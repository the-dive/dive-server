from dive.base_test import BaseTestWithDataFrameAndExcel, create_test_file
from apps.core.utils import create_dataset_and_tables
from apps.core.models import Snapshot
from apps.core.tasks import extract_table_data


class TestTasks(BaseTestWithDataFrameAndExcel):
    def test_extract_table_data(self):
        file_name = "test.xlsx"
        file_obj = create_test_file(self.excel_file_path, file_name=file_name)
        dataset = create_dataset_and_tables(file_obj)
        table = dataset.table_set.first()
        assert table is not None
        assert not Snapshot.objects.filter(table=table).exists()
        extract_table_data(table.id)
        snapshot = Snapshot.objects.filter(table=table).first()
        assert snapshot is not None
        assert snapshot.version == 1
