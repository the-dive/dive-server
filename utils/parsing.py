from typing import Type, Any, Optional

from .common import ColumnTypes


def parse(val: Optional[str], coltype: Any) -> str | int | float | None:
    # TODO: Integer/Float precision
    if coltype == ColumnTypes.INTEGER:
        return parse_int(val)
    elif coltype == ColumnTypes.FLOATING:
        return parse_float(val)
    return val and str(val)


def parse_type(typ: Type, val: Optional[str]):
    try:
        return typ(val)
    except (TypeError, ValueError):
        return None


def parse_int(val: Optional[str]):
    return parse_type(int, val)


def parse_float(val: Optional[str]):
    return parse_type(float, val)
