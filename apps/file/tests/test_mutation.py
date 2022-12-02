import json
import os

from graphene_file_upload.django.testing import GraphQLFileUploadTestCase

from django.conf import settings

from utils.graphene.tests import GraphQLTestCase

from apps.file.models import File
from dive.factories import UserFactory


class TestFileMutation(GraphQLFileUploadTestCase, GraphQLTestCase):
    def setUp(self):
        self.create_file = """
            mutation Mutation($data: CreateFileInputType!) {
                createFile(data: $data) {
                    ok
                    errors
                    result {
                      id
                      file
                      fileType
                    }
                }
            }
        """

        self.variables = {
            "data": {
                "file": None,
                "fileType": self.genum(File.Type.EXCEL),
            }
        }
        self.user = UserFactory.create()
        self.force_login(self.user)
        path = os.path.join(settings.TEST_DIR, "document")
        self.file = os.path.join(path, "test1.xlsx")
        super().setUp()

    def test_file_upload(self):

        with open(self.file, "rb") as t_file:
            response = self.client.post(
                "/graphql/",
                data={
                    "operations": json.dumps(
                        {"query": self.create_file, "variables": self.variables}
                    ),
                    "t_file": t_file,
                    "map": json.dumps({"t_file": ["variables.data.file"]}),
                },
            )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertTrue(content["data"]["createFile"]["ok"], content)
        self.assertIsNotNone(content["data"]["createFile"]["result"]["id"])
        self.assertIsNotNone(content["data"]["createFile"]["result"]["file"])
