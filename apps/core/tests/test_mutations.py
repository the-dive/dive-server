import os
import json
import shutil
import pandas as pd

from django.test import override_settings
from django.conf import settings

from graphene_file_upload.django.testing import GraphQLFileUploadTestCase

from utils.graphene.tests import GraphQLTestCase
from dive.factories import UserFactory
from dive.base_test import assert_object_created
from apps.core.models import Dataset, Table
from apps.core.factories import DatasetFactory, TableFactory


TEST_MEDIA_DIR = os.path.join(settings.TEST_DIR, "media")
TEST_FILE_PATH = os.path.join(settings.TEST_DIR, "documents", "test1.xlsx")

_pd_excel = pd.ExcelFile(TEST_FILE_PATH)
SHEETS_COUNT_IN_TEST_EXCEL = len(_pd_excel.sheet_names)


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class TestDatasetMutation(GraphQLFileUploadTestCase, GraphQLTestCase):
    def setUp(self):
        self.create_dataset = """
            mutation Mutation($data: CreateDatasetInputType!) {
                createDataset(data: $data) {
                    ok
                    errors
                    result {
                        id
                        name
                        status
                        tables {
                            id
                            name
                            status
                            isAddedToWorkspace
                        }
                    }
                }
            }
        """
        self.variables = {
            "data": {"file": None},
        }
        self.user = UserFactory.create()
        self.force_login(self.user)
        self.file = TEST_FILE_PATH
        super().setUp()

    def tearDown(self):
        # Remove the files in media
        try:
            shutil.rmtree(TEST_MEDIA_DIR)
        except Exception:
            pass

    @assert_object_created(Dataset, count=1)
    @assert_object_created(Table, count=SHEETS_COUNT_IN_TEST_EXCEL)
    def test_file_upload(self):
        content = self.call_create_dataset_api()
        data = content["data"]["createDataset"]
        self.assertTrue(data["ok"], content)
        result = data["result"]

        for field in ["id", "name", "status", "tables"]:
            self.assertIsNotNone(result[field])

        table_fields = ["id", "name", "status", "isAddedToWorkspace"]
        tables = result["tables"]
        assert (
            len(tables) > 0
        ), "There must be at least a table created for valid file upload"
        for table in tables:
            for field in table_fields:
                self.assertIsNotNone(table[field])

    def call_create_dataset_api(self):
        with open(self.file, "rb") as t_file:
            response = self.client.post(
                "/graphql/",
                data={
                    "operations": json.dumps(
                        {"query": self.create_dataset, "variables": self.variables}
                    ),
                    "file": t_file,
                    "map": json.dumps({"file": ["variables.data.file"]}),
                },
            )
        self.assertResponseNoErrors(response)
        return response.json()


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class TestTableMutation(GraphQLTestCase):
    def test_add_to_workspace(self):
        dataset = DatasetFactory.create(name="mydataset")
        table = TableFactory.create(dataset=dataset, is_added_to_workspace=False)
        mutate_query = """
            mutation Mutation($tableId: ID! $input: TableInputType!) {
                updateTable(id: $tableId data: $input) {
                    ok
                    errors
                    result {
                        id
                        name
                        isAddedToWorkspace
                    }
                }
            }
        """
        resp_data = self.query_check(
            mutate_query,
            minput={"isAddedToWorkspace": True},
            variables={"tableId": table.id},
        )
        content = resp_data["data"]["updateTable"]
        assert content["ok"] is True
        assert content["result"]["isAddedToWorkspace"] is True
        table = Table.objects.get(id=table.id)
        assert table.is_added_to_workspace is True

    def test_update_properties(self):
        dataset = DatasetFactory.create(name="mydataset")
        table = TableFactory.create(dataset=dataset, is_added_to_workspace=False)
        mutate_query = """
            mutation Mutation($tableId: ID! $input: TableInputType!) {
                updateTable(id: $tableId data: $input) {
                    ok
                    errors
                    result {
                        id
                        name
                        properties {
                            headerLevel
                        }
                    }
                }
            }
        """
        valid_props = {
            "headerLevel": "2",
            "timezone": "central",
            "language": "en",
            "trimWhitespaces": True,
        }

        resp_data = self.query_check(
            mutate_query,
            minput={"properties": valid_props},
            variables={"tableId": table.id},
        )
        content = resp_data["data"]["updateTable"]
        assert content["ok"] is True
        table = Table.objects.get(id=table.id)
        assert (
            content["result"]["properties"]["headerLevel"] == valid_props["headerLevel"]
        )

    def test_delete_table_from_workspace(self):
        dataset = DatasetFactory.create(name="mydataset")
        table = TableFactory.create(
            name="test",
            dataset=dataset,
            is_added_to_workspace=True,
        )
        query = """
            mutation Mutation($id: ID!) {
                deleteTableFromWorkspace(id: $id) {
                    ok
                    errors
                    result {
                        id
                        name
                        isAddedToWorkspace
                    }
                }
            }
        """
        resp_data = self.query_check(
            query,
            variables={"id": table.id},
        )
        content = resp_data["data"]["deleteTableFromWorkspace"]
        assert content["ok"] is True
        table = Table.objects.get(id=table.id)
        assert table.is_added_to_workspace is False

    def test_clone_table_from_workspace(self):
        dataset = DatasetFactory.create(name="mydataset")
        table = TableFactory.create(
            name="test",
            dataset=dataset,
            is_added_to_workspace=True,
        )
        old_table_count = Table.objects.count()
        query = """
            mutation Mutation($id: ID!) {
                cloneTable(id: $id) {
                    ok
                    errors
                    result {
                        id
                        name
                        isAddedToWorkspace
                        clonedFrom {
                            id
                            name
                        }
                    }
                }
            }
        """
        resp_data = self.query_check(
            query,
            variables={"id": table.id},
        )
        content = resp_data["data"]["cloneTable"]
        assert content["ok"] is True
        self.assertEqual(Table.objects.count(), old_table_count + 1)
        self.assertEqual(content["result"]["clonedFrom"]["name"], table.name)
        self.assertEqual(content["result"]["clonedFrom"]["id"], str(table.id))
