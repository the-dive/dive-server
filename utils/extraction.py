from typing import Tuple, Optional, Union, cast, Any, TypedDict, List, Type
import pandas as pd
import numpy as np

from .common import ColumnTypes
from apps.core.types import TablePropertiesDict


PreviewResult = Union[Tuple[dict, Optional[str]], Tuple[Optional[dict], str]]

ColumnObject = TypedDict(
    "ColumnObject", {"key": str, "label": str, "type": ColumnTypes}
)


def get_col_type_from_pd_type(pd_type):
    pd_type_str = str(pd_type)
    if "int" in pd_type_str:
        return ColumnTypes.INTEGER
    elif "float" in pd_type_str:
        return ColumnTypes.FLOATING
    elif "datetime" in pd_type_str:
        return ColumnTypes.DATETIME
    return ColumnTypes.STRING


def extract_preview_data(
    xl: pd.ExcelFile, sheetname: str, table_properties: TablePropertiesDict,
) -> PreviewResult:

    header_level = parse_int(table_properties["headerLevel"]) or 1
    # extract other header levels if header_level > 1
    extra_headers: dict = (
        extract_extra_headers(xl, sheetname, header_level)
        if header_level > 1
        else {}
    )

    df: pd.DataFrame = cast(pd.DataFrame, xl.parse(sheetname, nrows=50, header=header_level))
    na_replacement = {
        pd.NaT: None,
        np.nan: None,
        table_properties.get("treatTheseAsNa"): None,
    }

    df.replace(na_replacement, inplace=True)

    # Store map of column index and type information
    coltypes = {i: get_col_type_from_pd_type(t) for i, t in enumerate(df.dtypes)}

    df_dict = df.to_dict()

    columns: List[ColumnObject] = [
        {
            "key": str(i),
            "label": str(col),
            "type": coltypes[i],
        }
        for i, col in enumerate(df_dict.keys())
    ]

    def get_ith_row_from_df(i):
        # Add an attribute key to each the row item, it's okay if it is later replaced
        # It's just that we need to have a unique key field in each row
        row = {"key": i}
        for j, col in enumerate(df.columns):
            parsed = parse(df.loc[i, col], coltypes[j])
            should_strip = coltypes[j] == ColumnTypes.STRING and table_properties.get("trimWhitespaces", False)
            row[str(j)] = str(parsed).strip() if should_strip else parsed
        return row

    rows = [get_ith_row_from_df(i) for i in range(len(df))]

    return {
        "rows": rows,
        "columns": columns,
        "extra_headers": extra_headers,
    }, None


def extract_extra_headers(xl: pd.ExcelFile, sheetname: str, header_level: int):
    if header_level <= 1:
        # There's nothing to read before header 1
        return {}
    df: pd.DataFrame = cast(
        pd.DataFrame,
        xl.parse(sheetname, nrows=header_level - 1, header=None),
    )
    return df.to_dict()


def parse(val: Any, coltype: ColumnTypes) -> str | int | float | None:
    # TODO: Integer/Float precision
    if coltype == ColumnTypes.INTEGER:
        return parse_int(val)
    elif coltype == ColumnTypes.FLOATING:
        return parse_float(val)
    return val and str(val)


def parse_type(typ: Type, val: Any):
    try:
        return typ(val)
    except (TypeError, ValueError):
        return None


def parse_int(val: Any):
    return parse_type(int, val)


def parse_float(val: Any):
    return parse_type(float, val)
