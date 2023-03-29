from utils.graphene.tests import GraphQLTestCase

from dive.consts import LANGUAGES, TABLE_HEADER_ROWS, COLUMN_TYPES
from apps.core.factories import TableFactory, DatasetFactory
from apps.core.models import Table


class GlobalPropertiesTestCase(GraphQLTestCase):
    def test_global_properties_options(self):
        query = """
            query MyQuery {
                propertiesOptions {
                    table {
                        headerRows {
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
            len(response["data"]["propertiesOptions"]["table"]["headerRows"]),
            len(TABLE_HEADER_ROWS),
        )
        self.assertEqual(
            len(response["data"]["propertiesOptions"]["table"]["languages"]),
            len(LANGUAGES),
        )

    def test_column_properties_options(self):
        query = """
            query MyQuery {
                propertiesOptions {
                    column {
                        columnTypes {
                            key
                            label
                        }
                    }
                }
            }
        """
        response = self.query_check(query)
        self.assertEqual(
            len(response["data"]["propertiesOptions"]["column"]["columnTypes"]),
            len(COLUMN_TYPES),
        )


class TableTestCase(GraphQLTestCase):
    def test_table_filter(self):
        query = """
            query MyQuery($statuses: [TableStatusEnum!], $isAddedToWorkspace: Boolean) {
                tables(statuses: $statuses, isAddedToWorkspace: $isAddedToWorkspace) {
                    results {
                    id
                    name
                    isAddedToWorkspace
                    status
                    }
                }
            }
        """
        dataset = DatasetFactory.create()
        table1 = TableFactory.create(
            is_added_to_workspace=True,
            status=Table.TableStatus.PENDING,
            dataset=dataset,
        )
        table2 = TableFactory.create(
            is_added_to_workspace=True,
            status=Table.TableStatus.PENDING,
            dataset=dataset,
        )
        table3 = TableFactory.create(
            is_added_to_workspace=False,
            status=Table.TableStatus.EXTRACTED,
            dataset=dataset,
        )
        table4 = TableFactory.create(
            is_added_to_workspace=False,
            status=Table.TableStatus.EXTRACTED,
            dataset=dataset,
        )
        table5 = TableFactory.create(
            is_added_to_workspace=True,
            status=Table.TableStatus.PENDING,
            dataset=dataset,
        )

        filter_data = {"isAddedToWorkspace": True}
        content = self.query_check(query, variables={**filter_data})
        self.assertListIds(
            content["data"]["tables"]["results"], [table1, table2, table5]
        )

        filter_data.pop("isAddedToWorkspace")
        filter_data = {"statuses": [self.genum(Table.TableStatus.EXTRACTED)]}
        content = self.query_check(query, variables={**filter_data})
        self.assertListIds(content["data"]["tables"]["results"], [table3, table4])
