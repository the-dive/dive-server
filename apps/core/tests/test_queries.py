import os
import shutil
import pandas as pd

from utils.graphene.tests import GraphQLTestCase
from django.test import override_settings
from django.conf import settings

from apps.file.utils import create_dataset_and_tables

from .utils import create_test_file


TEST_MEDIA_DIR = os.path.join(settings.TEST_DIR, "media")
TEST_FILE_PATH = os.path.join(settings.TEST_DIR, "documents", "test1.xlsx")

_pd_excel = pd.ExcelFile(TEST_FILE_PATH)
SHEETS_COUNT_IN_TEST_EXCEL = len(_pd_excel.sheet_names)


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class TestDatasetQuery(GraphQLTestCase):
    def setUp(self):
        self.dataset_query = """
            query GetDataset($id: ID!) {
                dataset(id: $id) {
                    id
                    name
                    tables {
                        id
                        name
                    }
                }
            }
        """
        self.table_query = """
            query GetTable($id: ID!) {
                table(id: $id) {
                    id
                    name
                    isAddedToWorkspace
                    previewData
                }
            }
        """
        super().setUp()

    def tearDown(self):
        # Remove the files in media
        try:
            shutil.rmtree(TEST_MEDIA_DIR)
        except Exception:
            pass

    def test_get_dataset(self):
        # Create dataset first
        file_name = "test.xlsx"
        file_obj = create_test_file(TEST_FILE_PATH, file_name=file_name)
        dataset = create_dataset_and_tables(file_obj)
        content = self.query_check(self.dataset_query, variables={"id": dataset.pk})
        data = content["data"]["dataset"]
        assert data["id"] == str(dataset.pk)
        tables = data["tables"]
        assert len(tables) == SHEETS_COUNT_IN_TEST_EXCEL

    def test_get_table(self):
        file_obj = create_test_file(TEST_FILE_PATH)
        dataset = create_dataset_and_tables(file_obj)
        table = dataset.table_set.first()
        content = self.query_check(
            self.table_query,
            variables={"id": table.pk},
        )
        table_resp = content["data"]["table"]
        assert table_resp["name"] == table.name
        preview_data = table_resp["previewData"]
        assert "rows" in preview_data
        assert "columns" in preview_data

        assert len(preview_data["rows"]) > 0, "There should be some rows"
        for row in preview_data["rows"]:
            assert "key" in row, "Each row should have a key field"

        assert len(preview_data["columns"]) > 0, "There should be some cols"
        for col in preview_data["columns"]:
            assert "type" in col
            assert "label" in col
            assert "key" in col
