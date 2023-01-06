import os
import pandas as pd

from dive.base_test import BaseAPITestCase
from apps.core.validators import get_default_table_properties
from utils.extraction import extract_preview_data_from_excel
from utils.common import ColumnTypes


NUM_ROWS = 10
DATA = {
    "id": [x for x in range(1, NUM_ROWS + 1)],
    "name": ["Sam", "Morgan", "Rishi", "Shreeyash", "Sameer", "Bibek", "", "Patrice", "Ram", "Sita"],
    "income": [x * 2000 for x in range(1, NUM_ROWS + 1)],
}

DATAFRAME = pd.DataFrame(data=DATA)


class TestExtraction(BaseAPITestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_table_properties = get_default_table_properties()

    def setUp(self):
        self.excel_file_path = 'test_result.xlsx'
        DATAFRAME.to_excel(self.excel_file_path, index=False)

    def valid_parse_excel(self, properties):
        """
        Parse excel and perform basic assertations.
        Returns: (preview_data, error)
        """
        xl = pd.ExcelFile(self.excel_file_path)
        sheetname = xl.sheet_names[0]
        preview_data, err = extract_preview_data_from_excel(xl, sheetname, properties)

        assert err is None, "There should be no error"
        assert preview_data is not None, "There should be preview data"
        return preview_data, err

    def test_extract_preview_data_excel_default_props(self):
        preview_data, _ = self.valid_parse_excel(self.default_table_properties)
        extra_headers = preview_data["extra_headers"]
        assert extra_headers == [], "There are no extra headers"

        # validate columns
        expected_columns = [
            {"key": "0", "label": "id", "type": ColumnTypes.INTEGER},
            {"key": "1", "label": "name", "type": ColumnTypes.STRING},
            {"key": "2", "label": "income", "type": ColumnTypes.INTEGER},
            # NOTE: If you look at the income column, there is .40, this is to make
            # it parse as floating type. just having .00 parses it as integer
        ]
        columns = preview_data["columns"]
        assert len(columns) == len(DATA.keys()), "Number of columns should match"
        assert columns == expected_columns

        # validate rows
        rows = preview_data["rows"]
        assert len(rows) == NUM_ROWS, f"There must be {NUM_ROWS} rows"
        row2 = rows[1]
        assert row2["1"] == "Morgan", "Checking random cell should match"
        assert {"key", "0", "1", "2"} == set(row2.keys()), \
            "Row key and column indices should be present as keys in row"

    def test_extract_preveiw_data_excel_header_2(self):
        """Testing extraction with header level 2"""
        props = {
            **self.default_table_properties,
            "headerLevel": "2"
        }
        preview_data, _ = self.valid_parse_excel(props)

        # validate columns
        expected_columns = [
            {"key": "0", "label": "2", "type": ColumnTypes.INTEGER},
            {"key": "1", "label": "Morgan", "type": ColumnTypes.STRING},
            {"key": "2", "label": "4000", "type": ColumnTypes.INTEGER},
            # NOTE: If you look at the income column, there is .40, this is to make
            # it parse as floating type. just having .00 parses it as integer
        ]
        columns = preview_data["columns"]
        assert len(columns) == len(DATA.keys()), "Number of columns should match"
        assert columns == expected_columns

        # validate rows
        rows = preview_data["rows"]
        assert len(rows) == NUM_ROWS - 2, "There must be 2 less rows as header is at index 2"

        # validate extra headers
        extra_headers = preview_data["extra_headers"]
        expected_extra_headers = [
            ["id", "name", "income"],
            ["1", "Sam", "2000"],
        ]
        assert extra_headers == expected_extra_headers, "Extra headers should be present"

    def test_extract_preveiw_data_excel_treat_NA(self):
        """Test NA values"""
        props = {
            **self.default_table_properties,
            "treatTheseAsNa": "Sita",
        }
        preview_data, _ = self.valid_parse_excel(props)

        # validate rows
        rows = preview_data["rows"]
        assert len(rows) == NUM_ROWS
        last_row = rows[-1]
        assert last_row["1"] is None, "'Sita' should have been treated as NA"

    def tearDown(self):
        if os.path.exists(self.excel_file_path):
            os.remove(self.excel_file_path)
