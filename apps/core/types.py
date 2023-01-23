from typing import TypedDict, Optional, List, Dict, Any

from utils.common import ColumnTypes


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
