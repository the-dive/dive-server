from dive.consts import TABLE_HEADER_LEVELS, TIMEZONES, LANGUAGES


table_properties_schema = {
    "title": "Table Properties",
    "properties": {
        "header_level": {
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
        "trim_whitespaces": {
            "type": "boolean",
        },
        "treat_these_as_na": {
            "type": ["string", "null"],
        }
    },
    "required": ["header_level", "timezone", "language", "trim_whitespaces"],
}
