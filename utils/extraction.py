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

from .common import ColumnTypes
from .parsing import parse_int, parse
from apps.core.types import TablePropertiesDict, ExtractedData, ColumnStats, Column


PreviewResult = Union[
    Tuple[ExtractedData, Optional[str]], Tuple[Optional[ExtractedData], str]
]

INFINITY = 999999


def get_col_type_from_pd_type(pd_type) -> ColumnTypes:
    pd_type_str = str(pd_type)
    if "int" in pd_type_str:
        return ColumnTypes.INTEGER
    elif "float" in pd_type_str:
        return ColumnTypes.FLOATING
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

    # Store map of column index and type information
    coltypes: Dict[int, ColumnTypes] = {i: get_col_type_from_pd_type(t) for i, t in enumerate(df.dtypes)}

    df_dict: Dict[str, list] = df.to_dict("list")

    columns: List[Column] = [
        {
            "key": str(i),
            "label": str(col),
            "type": coltypes[i],
        }
        for i, col in enumerate(df_dict.keys())
    ]

    trimWhitespaces = table_properties.get("trimWhitespaces", False)

    def get_ith_row_from_df(i):
        # Add an attribute key to each the row item, it's okay if it is later replaced
        # It's just that we need to have a unique key field in each row
        row: Dict[str, Any] = {"key": str(i)}
        for j, col in enumerate(df.columns):
            val = df.loc[i, col]
            parsed = parse(val, coltypes[j])
            should_strip = coltypes[j] == ColumnTypes.STRING and trimWhitespaces
            row[str(j)] = str(parsed).strip() if should_strip else parsed
        return row

    rows = [get_ith_row_from_df(i) for i in range(len(df))]

    extracted: ExtractedData = {
        "rows": rows,
        "columns": columns,
        "extra_headers": extra_headers,
        "column_stats": calculate_column_stats(df_dict, coltypes)
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


def calculate_column_stats(df_dict: dict, coltypes: Dict[int, ColumnTypes]):
    """
    Calculate column wise stats.
    df_dict is a dict of the form:
        {
            col1: [item1, item2, ...],
            col2: [item1, item2, ...],
        }
    which is the result of dataframe.to_dict()
    """
    column_stats = []
    for index, (colname, coltype) in enumerate(zip(df_dict.keys(), coltypes.values())):
        if coltype == ColumnTypes.INTEGER:
            stats_data = calculate_stats_for_numeric_col(df_dict[colname])
        elif coltype == ColumnTypes.FLOATING:
            stats_data = calculate_stats_for_numeric_col(df_dict[colname])
        else:
            stats_data = calculate_stats_for_string_col(df_dict[colname])

        column_info = {
            **stats_data,
            "key": str(index),
            "label": colname,
            "type": coltype,
        }
        column_stats.append(column_info)
    return column_stats


def calculate_stats_for_numeric_col(items: list) -> ColumnStats:
    # TODO: optimize the list(use np/pd). But this should happen from the extraction phase itself
    return {
        "min": float(np.min(items)),
        "max": float(np.max(items)),
        "mean": float(np.mean(items)),
        "median": float(np.median(items)),
        "std_deviation": float(np.std(items)),
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
    return {
        "total_count": len(items),
        "na_count": len([x for x in items if x is None]),
        "unique_count": len(set(items)),
        "max_length": max_len,
        "min_length": min_len,
    }
