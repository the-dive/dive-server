from jsonschema import validate, ValidationError as JSONValidationError
from django.core.exceptions import ValidationError

from dive.consts import TABLE_HEADER_LEVELS, TIMEZONES, LANGUAGES


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
        }
    },
    "required": ["headerLevel", "timezone", "language", "trimWhitespaces"],
}


def validate_table_properties(properties: dict):
    try:
        validate(properties, table_properties_schema)
    except JSONValidationError as e:
        msg = e.message[:200] + "..." if len(e.message) > 200 else e.message
        raise ValidationError(f"Invalid properties data: {msg}")
