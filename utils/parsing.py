from typing import Type, Any

from .common import ColumnTypes


def parse(val: Any, coltype: Any) -> str | int | float | None:
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
