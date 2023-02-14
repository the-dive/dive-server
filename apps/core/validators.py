from jsonschema import validate, ValidationError as JSONValidationError
from django.core.exceptions import ValidationError

from dive.consts import (
    TABLE_HEADER_LEVELS,
    TIMEZONES,
    LANGUAGES,
    JOIN_CLAUSE_OPERATIONS,
)
from .types import TablePropertiesDict


table_properties_schema = {
    "title": "Table Properties",
    "properties": {
        "headerLevel": {
            "type": "string",
            "enum": [x["key"] for x in TABLE_HEADER_LEVELS],
        },
        "timezone": {
            "type": "string",
            "enum": [x["key"] for x in TIMEZONES],
        },
        "language": {
            "type": "string",
            "enum": [x[0] for x in LANGUAGES],
        },
        "trimWhitespaces": {
            "type": "boolean",
        },
        "treatTheseAsNa": {
            "type": ["string", "null"],
        },
    },
    "required": ["headerLevel", "timezone", "language", "trimWhitespaces"],
}

join_clause_schema = {
    "type": "array",
    "items": {
        "additionalProperties": False,
        "properties": {
            "source_column": {
                "type": "string",
            },
            "target_column": {
                "type": "string",
            },
            "operation": {
                "type": "string",
                "enum": [x for x in JOIN_CLAUSE_OPERATIONS.values],
            },
        },
        "required": ["source_column", "target_column", "operation"],
    },
}


def get_default_table_properties() -> TablePropertiesDict:
    return {
        "headerLevel": "0",
        "timezone": "UTC",
        "language": "en",
        "trimWhitespaces": False,
        "treatTheseAsNa": "",
    }


def validate_table_properties(properties: dict):
    try:
        validate(properties, table_properties_schema)
    except JSONValidationError as e:
        msg = e.message[:200] + "..." if len(e.message) > 200 else e.message
        raise ValidationError(f"Invalid properties data: {msg}")
