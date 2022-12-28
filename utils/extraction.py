from typing import Tuple, Optional, Union, cast, Any, TypedDict, List, Type
import pandas as pd
import numpy as np

from .common import ColumnTypes


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
    xl: pd.ExcelFile, sheetname: str, table_properties=None
) -> PreviewResult:
    df: pd.DataFrame = cast(pd.DataFrame, xl.parse(sheetname, nrows=50, header=1))
    df.replace({pd.NaT: None, np.nan: None}, inplace=True)

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
            row[str(j)] = parse(df.loc[i, col], coltypes[j])
        return row

    rows = [get_ith_row_from_df(i) for i in range(len(df))]

    return {
        "rows": rows,
        "columns": columns,
    }, None


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
