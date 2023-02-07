from typing import TypedDict, Optional, List, Dict, Any, Tuple, Union

from utils.common import ColumnTypes


Validation = Tuple[bool, Optional[str]]


class TablePropertiesDict(TypedDict):
    headerLevel: str
    timezone: str
    language: str
    trimWhitespaces: bool
    treatTheseAsNa: Optional[str]


class Column(TypedDict):
    key: str
    label: str
    type: ColumnTypes


class ExtractedData(TypedDict):
    rows: List[Dict[str, Any]]
    columns: List[Column]
    extra_headers: List[List[str]]
    column_stats: Any  # TODO


class NumericColumnStats(TypedDict):
    min: float
    max: float
    mean: float
    median: float
    std_deviation: float
    total_count: int
    na_count: int


class StringColumnStats(TypedDict):
    total_count: int
    na_count: int
    unique_count: int
    max_length: int
    min_length: int


ColumnStats = Union[NumericColumnStats, StringColumnStats]
