from typing import Type, Any, Optional

import dateparser

from .common import ColumnTypes, float_r


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
    elif coltype == ColumnTypes.NUMBER:
        return parse_int(strval) or parse_float(strval)
    elif coltype == ColumnTypes.DATE:
        return parse_date(strval)
    elif coltype == ColumnTypes.DATETIME:
        return parse_datetime(strval)
    return strval


def parse_type(typ: Type, val: Optional[str]):
    try:
        return typ(val)
    except (TypeError, ValueError):
        return None


def parse_int(val: Optional[str]) -> Optional[int]:
    return parse_type(int, val)


def parse_float(val: Optional[str]) -> Optional[float]:
    return parse_type(float_r, val)


def parse_datetime(val: Optional[str]) -> Optional[str]:
    """Parse input value to datetime and return iso string if parsed"""
    # TODO: add formatting
    if val is None:
        return None
    date = dateparser.parse(val)
    return date and date.isoformat()


def parse_date(val: Optional[str]) -> Optional[str]:
    """Parse input value to date and return iso string if parsed"""
    # TODO: add formatting
    if val is None:
        return None
    date = dateparser.parse(val)
    return date and date.isoformat()[:10]
