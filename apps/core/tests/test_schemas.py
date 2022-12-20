from utils.graphene.tests import GraphQLTestCase

from dive.consts import LANGUAGES, TABLE_HEADER_LEVELS


class GlobalPropertiesTestCase(GraphQLTestCase):
    def test_global_properties(self):
        query = """
            query MyQuery {
                properties {
                    table {
                        headers {
                            key
                            label
                        }
                        languages {
                            key
                            label
                        }
                        timeZones {
                            key
                            label
                        }
                    }
                }
            }
        """
        response = self.query_check(query)
        self.assertEqual(
            len(response["data"]["properties"]["table"]["headers"]),
            len(TABLE_HEADER_LEVELS),
        )
        self.assertEqual(
            len(response["data"]["properties"]["table"]["languages"]), len(LANGUAGES)
        )
