from utils.graphene.tests import GraphQLTestCase

from dive.consts import LANGUAGES, TABLE_HEADER_LEVELS


class GlobalPropertiesTestCase(GraphQLTestCase):
    def test_global_properties_options(self):
        query = """
            query MyQuery {
                propertiesOptions {
                    table {
                        headerLevels {
                            key
                            label
                        }
                        languages {
                            key
                            label
                        }
                        timezones {
                            key
                            label
                        }
                    }
                }
            }
        """
        response = self.query_check(query)
        self.assertEqual(
            len(response["data"]["propertiesOptions"]["table"]["headerLevels"]),
            len(TABLE_HEADER_LEVELS),
        )
        self.assertEqual(
            len(response["data"]["propertiesOptions"]["table"]["languages"]), len(LANGUAGES)
        )
