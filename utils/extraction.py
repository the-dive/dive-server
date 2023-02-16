from typing import (
    Tuple,
    Optional,
    Union,
    cast,
    Any,
    List,
    Dict,
)
import pandas as pd
import numpy as np

from .common import ColumnTypes, float_r
from .parsing import parse_int, parse
from apps.core.types import TablePropertiesDict, ExtractedData, ColumnStats, Column


PreviewResult = Union[
    Tuple[ExtractedData, Optional[str]], Tuple[Optional[ExtractedData], str]
]

INFINITY = float("inf")


def get_col_type_from_pd_type(pd_type) -> ColumnTypes:
    pd_type_str = str(pd_type)
    if "int" in pd_type_str:
        return ColumnTypes.INTEGER
    elif "float" in pd_type_str:
        return ColumnTypes.FLOAT
    elif "datetime" in pd_type_str:
        return ColumnTypes.DATETIME
    return ColumnTypes.STRING


def extract_preview_data_from_excel(
    xl: pd.ExcelFile,
    sheetname: str,
    table_properties: TablePropertiesDict,
) -> PreviewResult:
    return extract_data_from_excel(xl, sheetname, table_properties, is_preview=True)


def extract_data_from_excel(
    xl: pd.ExcelFile,
    sheetname: str,
    table_properties: TablePropertiesDict,
    is_preview: bool = False,
    calculate_stats=False,
) -> PreviewResult:
    header_level = parse_int(table_properties["headerLevel"]) or 0
    # extract and save other header levels if header_level >= 1
    extra_headers: List[List[str]] = (
        extract_extra_headers(xl, sheetname, header_level) if header_level > 0 else []
    )

    df: pd.DataFrame = cast(
        pd.DataFrame,
        xl.parse(
            sheetname,
            nrows=50 if is_preview else None,
            header=header_level,
        ),
    )
    na_replacement = {
        pd.NaT: None,
        np.nan: None,
        table_properties.get("treatTheseAsNa"): None,
    }

    df.replace(na_replacement, inplace=True)

    columns: List[Column] = [
        {"key": str(i), "label": str(col), "type": get_col_type_from_pd_type(coltype)}
        for i, (col, coltype) in enumerate(zip(df.columns, df.dtypes))
    ]

    trimWhitespaces = table_properties.get("trimWhitespaces", False)

    def get_ith_row_from_df(i):
        # Add an attribute key to each the row item, it's okay if it is later replaced
        # It's just that we need to have a unique key field in each row
        row: Dict[str, Any] = {"key": str(i)}
        for j, col in enumerate(columns):
            val = df.iloc[i, j]
            parsed = parse(val, col["type"])
            should_strip = col["type"] == ColumnTypes.STRING and trimWhitespaces
            row[col["key"]] = str(parsed).strip() if should_strip else parsed
        return row

    rows = [get_ith_row_from_df(i) for i in range(len(df))]

    extracted: ExtractedData = {
        "rows": rows,
        "columns": columns,
        "extra_headers": extra_headers,
        "column_stats": calculate_column_stats(rows, columns)
        if calculate_stats
        else None,
    }
    return extracted, None


def extract_extra_headers(
    xl: pd.ExcelFile, sheetname: str, header_level: int
) -> List[List[str]]:
    if header_level < 1:
        # There's nothing to read before header 1
        return []
    df: pd.DataFrame = cast(
        pd.DataFrame,
        xl.parse(
            sheetname,
            nrows=header_level,
            header=None,
        ),
    )
    return [[str(e) for e in row] for row in df.itertuples(index=False)]


def calculate_column_stats(data_rows: List[Dict[str, Any]], columns: List[Column]):
    """
    Calculate column wise stats.
    data_rows is a list of the form:
        [
            { col1: val1, col2: val2, ...}
            ...
        ]
    which is the result of dataframe.to_dict()
    """
    column_stats = []
    for col in columns:
        colkey = col["key"]
        col_items = [row[colkey] for row in data_rows]
        single_column_stats = calculate_single_column_stats(col_items, col["type"])
        column_info = {
            **single_column_stats,
            **col,
        }
        column_stats.append(column_info)
    return column_stats


def calculate_single_column_stats(items: list, coltype: ColumnTypes) -> ColumnStats:
    if coltype == ColumnTypes.INTEGER:
        return calculate_stats_for_numeric_col(items)
    elif coltype == ColumnTypes.FLOAT:
        return calculate_stats_for_numeric_col(items)
    else:
        return calculate_stats_for_string_col(items)


def calculate_stats_for_numeric_col(items: list) -> ColumnStats:
    # TODO: optimize the list(use np/pd). But this should happen from the extraction phase itself
    return {
        "min": float_r(np.min(items)),
        "max": float_r(np.max(items)),
        "mean": float_r(np.mean(items)),
        "median": float_r(np.median(items)),
        "std_deviation": float_r(np.std(items)),
        "total_count": len(items),
        "na_count": len([x for x in items if x is None]),
    }


def calculate_stats_for_string_col(items: list) -> ColumnStats:
    max_len = 0
    min_len = INFINITY
    for x in items:
        if x is None:
            continue
        length = len(x)
        if length > max_len:
            max_len = length
        if length < min_len:
            min_len = length

    # TODO: optimize the following calculations
    non_null_items = [x for x in items if x is None]
    return {
        "total_count": len(items),
        "na_count": len(non_null_items),
        "unique_count": len(set(non_null_items)),
        "max_length": max_len,
        "min_length": 0 if min_len == INFINITY else int(min_len),
        # NOTE: Need to cast min_length to int although it is guranteed to be an int becauese of mypy error
    }
