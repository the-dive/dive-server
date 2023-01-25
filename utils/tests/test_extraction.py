import os
import pandas as pd

from django.test import override_settings
from django.conf import settings

from dive.base_test import BaseTestWithDataFrameAndExcel, DATA, NUM_ROWS
from utils.extraction import extract_data_from_excel
from utils.common import ColumnTypes

TEST_MEDIA_DIR = os.path.join(settings.TEST_DIR, "media")


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class TestExtraction(BaseTestWithDataFrameAndExcel):
    def parse_excel_and_check_valid(
        self, properties, is_preview=True, calculate_stats=False
    ):
        """
        Parse excel and perform basic assertations.
        Returns: (preview_data, error)
        """
        xl = pd.ExcelFile(self.excel_file_path)
        sheetname = xl.sheet_names[0]
        data, err = extract_data_from_excel(
            xl,
            sheetname,
            properties,
            is_preview=is_preview,
            calculate_stats=calculate_stats,
        )

        assert err is None, "There should be no error"
        assert data is not None, "There should be preview data"
        return data, err

    def test_extract_preview_data_excel_default_props(self):
        preview_data, _ = self.parse_excel_and_check_valid(
            self.default_table_properties
        )
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
        assert {"key", "0", "1", "2"} == set(
            row2.keys()
        ), "Row key and column indices should be present as keys in row"

    def test_extract_preveiw_data_excel_header_2(self):
        """Testing extraction with header level 2"""
        props = {**self.default_table_properties, "headerLevel": "2"}
        preview_data, _ = self.parse_excel_and_check_valid(props)

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
        assert (
            len(rows) == NUM_ROWS - 2
        ), "There must be 2 less rows as header is at index 2"

        # validate extra headers
        extra_headers = preview_data["extra_headers"]
        expected_extra_headers = [
            ["id", "name", "income"],
            ["1", "Sam", "2000"],
        ]
        assert (
            extra_headers == expected_extra_headers
        ), "Extra headers should be present"

    def test_extract_preveiw_data_excel_treat_NA(self):
        """Test NA values"""
        props = {
            **self.default_table_properties,
            "treatTheseAsNa": "Sita",
        }
        preview_data, _ = self.parse_excel_and_check_valid(props)

        # validate rows
        rows = preview_data["rows"]
        assert len(rows) == NUM_ROWS
        last_row = rows[-1]
        assert last_row["1"] is None, "'Sita' should have been treated as NA"

    def test_extract_with_column_stats(self):
        props = {**self.default_table_properties, "headerLevel": "1"}
        extraction_data, _ = self.parse_excel_and_check_valid(
            props, is_preview=False, calculate_stats=True
        )
        assert "rows" in extraction_data
        assert "columns" in extraction_data
        assert extraction_data.get("column_stats") is not None

        # NOTE: The following are dependent on the global DATA defined in the beginning of this file
        id_stats = extraction_data["column_stats"][0]
        name_stats = extraction_data["column_stats"][1]
        income_stats = extraction_data["column_stats"][2]
        assert set(id_stats.keys()) == {
            "min",
            "max",
            "mean",
            "median",
            "total_count",
            "std_deviation",
            "na_count",
        }
        assert set(income_stats.keys()) == {
            "min",
            "max",
            "mean",
            "median",
            "total_count",
            "std_deviation",
            "na_count",
        }
        assert set(name_stats.keys()) == {
            "total_count",
            "na_count",
            "unique_count",
            "max_length",
            "min_length",
        }

    def tearDown(self):
        if os.path.exists(self.excel_file_path):
            os.remove(self.excel_file_path)
