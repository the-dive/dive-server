from typing import Any
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


def array_of(schema):
    return {"type": "array", "items": schema}


column_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "key": {"type": "string"},
        "label": {"type": "string"},
        "type": {"type": "string"},
    },
}


table_preview_schema = {
    "schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "items": {
        "additionalProperties": False,
        "properties": {
            "columns": array_of(column_schema),
            "rows": array_of(
                {
                    "type": "object",
                }
            ),
        },
        "required": ["columns", "rows"],
    },
}

join_clause_schema = {
    "schema": "http://json-schema.org/draft-07/schema#",
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
    return validate_with_schema(table_properties_schema)(properties)


def validate_join_clauses(clauses: list):
    return validate_with_schema(join_clause_schema)(clauses)


def validate_table_preview(data: dict):
    return validate_with_schema(table_preview_schema)(data)


def validate_with_schema(schema: Any):
    def validator(data):
        try:
            validate(data, schema)
        except JSONValidationError as e:
            msg = e.message[:200] + "..." if len(e.message) > 200 else e.message
            raise ValidationError(f"Invalid data: {msg}")

    return validator
