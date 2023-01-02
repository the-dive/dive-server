from typing import TypedDict, Optional


class TablePropertiesDict(TypedDict):
    headerLevel: str
    timezone: str
    language: str
    trimWhitespaces: bool
    treatTheseAsNa: Optional[str]
