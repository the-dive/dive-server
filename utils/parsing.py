from typing import Type, Any, Optional

from .common import ColumnTypes


def parse(val: Optional[Any], coltype: Any) -> str | int | float | None:
    # TODO: Integer/Float precision
    if val is None:
        return None
    # Convert to string first
    strval = str(val)
    if coltype == ColumnTypes.INTEGER:
        return parse_int(strval)
    elif coltype == ColumnTypes.FLOAT:
        return parse_float(strval)
    return strval


def parse_type(typ: Type, val: Optional[str]):
    try:
        return typ(val)
    except (TypeError, ValueError):
        return None


def parse_int(val: Optional[str]):
    return parse_type(int, val)


def parse_float(val: Optional[str]):
    return parse_type(float, val)
