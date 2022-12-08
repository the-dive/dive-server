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
        content = response.json()
        self.assertResponseNoErrors(response)
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
