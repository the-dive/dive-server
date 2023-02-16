import json
import shutil
import pandas as pd

from unittest import mock
from django.test import override_settings, TestCase

from graphene_file_upload.django.testing import GraphQLFileUploadTestCase

from utils.graphene.tests import GraphQLTestCase
from dive.factories import UserFactory
from dive.base_test import (
    assert_object_created,
    TEST_MEDIA_DIR,
    TEST_FILE_PATH,
    BaseTestWithDataFrameAndExcel,
)
from apps.core.models import Dataset, Table, Action, Join
from apps.core.tasks import create_snapshot_for_table
from apps.core.factories import DatasetFactory, TableFactory

from dive.base_test import create_test_file


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
        self.file_path = TEST_FILE_PATH
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
        with open(self.file_path, "rb") as t_file:
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
    @mock.patch("apps.core.mutations.extract_table_data.delay")
    def test_add_to_workspace(self, extraction_task_func):
        dataset = DatasetFactory.create(name="mydataset")
        table = TableFactory.create(dataset=dataset, is_added_to_workspace=False)
        mutate_query = """
            mutation Mutation($tableId: ID! $isAddedToWorkspace: Boolean!) {
                addTableToWorkspace(id: $tableId isAddedToWorkspace: $isAddedToWorkspace) {
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
            variables={"tableId": table.id, "isAddedToWorkspace": True},
        )
        content = resp_data["data"]["addTableToWorkspace"]
        assert content["ok"] is True
        assert content["result"]["isAddedToWorkspace"] is True
        table = Table.objects.get(id=table.id)
        assert table.is_added_to_workspace is True
        extraction_task_func.assert_called_once_with(table.id)

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

    @assert_object_created(Table, count=2)
    def test_clone_table_from_workspace(self):
        dataset = DatasetFactory.create(name="mydataset")
        table = TableFactory.create(
            name="test",
            dataset=dataset,
            is_added_to_workspace=True,
        )
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
        self.assertEqual(content["result"]["clonedFrom"]["name"], table.name)
        self.assertEqual(content["result"]["clonedFrom"]["id"], str(table.id))

    @mock.patch("apps.core.mutations.apply_table_properties_and_extract_preview")
    def test_update_table_properties(self, apply_table_properties_func):
        file = create_test_file(TEST_FILE_PATH)
        dataset = DatasetFactory.create(name="mydataset", file=file)
        table = TableFactory.create(dataset=dataset, is_added_to_workspace=False)
        mutate_query = """
            mutation Mutation($tableId: ID! $input: TablePropertiesInputType!) {
                updateTableProperties(id: $tableId data: $input) {
                    ok
                    errors
                    result {
                        id
                        name
                        isAddedToWorkspace
                        properties {
                            headerLevel
                            language
                            timezone
                            trimWhitespaces
                            treatTheseAsNa
                        }
                    }
                }
            }
        """
        data = {
            "headerLevel": "2",
            "timezone": "UTC",
            "language": "en",
            "trimWhitespaces": True,
            "treatTheseAsNa": "",
        }
        resp_data = self.query_check(
            mutate_query,
            minput=data,
            variables={"tableId": table.id},
        )
        content = resp_data["data"]["updateTableProperties"]
        assert content["ok"] is True
        apply_table_properties_func.assert_called_once_with(table)
        self.assertEqual(content["result"]["properties"], data)

    def test_rename_table(self):
        dataset = DatasetFactory.create(name="mydataset")
        table = TableFactory.create(
            dataset=dataset,
            is_added_to_workspace=False,
            name="Test Table",
        )
        mutate_query = """
            mutation Mutation($tableId: ID! $name: String!) {
                renameTable(id: $tableId name: $name) {
                    ok
                    errors
                    result {
                        id
                        name
                    }
                }
            }
        """
        variables = {"tableId": table.id, "name": "New Table"}
        resp_data = self.query_check(
            mutate_query,
            variables=variables,
        )
        content = resp_data["data"]["renameTable"]
        assert content["ok"] is True
        self.assertEqual(content["result"]["name"], variables["name"])


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class TestTableActions(GraphQLTestCase, BaseTestWithDataFrameAndExcel, TestCase):
    def setUp(self):
        super().setUp()
        self.action_mutation = """
            mutation Mutation($tableId: ID! $action: ActionInputType!) {
                tableAction(id: $tableId action: $action) {
                    ok
                    errors
                }
            }
        """
        self.table = self.dataset.table_set.first()
        col_key = "0"
        self.variables = {
            "tableId": self.table.id,
            "action": {
                "actionName": "cast_column",
                "params": [col_key, "string"],
            },
        }

    @mock.patch("apps.core.mutations.calculate_column_stats_for_action.delay")
    def test_table_action_mutation(self, col_stats_delay_func):
        # First create snapshot for table
        create_snapshot_for_table(self.table)

        with self.captureOnCommitCallbacks(execute=True):
            resp_data = self.query_check(
                self.action_mutation,
                variables=self.variables,
            )
        content = resp_data["data"]["tableAction"]
        assert content["ok"] is True
        new_action = Action.objects.filter(order=1, table=self.table).last()
        assert new_action is not None
        col_stats_delay_func.assert_called_with(new_action.pk)


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class TestTableJoinMutation(GraphQLTestCase, BaseTestWithDataFrameAndExcel, TestCase):
    def setUp(self):
        super().setUp()
        self.join_mutation = """
            mutation Mutation($tableId: ID! $data: TableJoinInputType!) {
                tableJoin(id: $tableId, data: $data) {
                    ok
                    errors
                    result {
                        joinedFrom {
                            id
                            targetTable {
                                id
                            }
                            sourceTable {
                                id
                            }
                        }
                        originalName
                        id
                    }
                }
            }
        """
        self.source_table = TableFactory.create(name="Source Table")
        self.target_table = TableFactory.create(name="Target Table")
        self.variables = {
            "tableId": self.source_table.id,
            "data": {
                "targetTable": self.target_table.id,
                "joinType": self.genum(Join.JoinType.INNER_JOIN),
                "clauses": json.dumps(
                    {
                        "source_column": "person_id",
                        "target_column": "id",
                        "operator": "equal",
                    }
                ),
            },
        }

    @mock.patch("apps.core.mutations.perform_join.delay")
    def test_table_join(self, table_join_delay_func):
        with self.captureOnCommitCallbacks(execute=True):
            resp_data = self.query_check(
                self.join_mutation,
                variables=self.variables,
            )
        content = resp_data["data"]["tableJoin"]
        assert content["ok"] is True
        table_join_delay_func.assert_called_with(int(content["result"]["id"]))
