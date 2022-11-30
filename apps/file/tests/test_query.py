from utils.graphene.tests import GraphQLTestCase

from apps.file.factories import FileFactory


class FileQuery(GraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.file_query = """
            query MyQuery {
              files {
                results {
                  id
                  file
                }
                totalCount
              }
            }
        """

    def test_file_query(self):
        FileFactory.create()
        content = self.query_check(self.file_query)
        self.assertEqual(content["data"]["files"]["totalCount"], 1)
