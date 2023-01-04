from jsonschema import validate, ValidationError as JSONValidationError
from rest_framework import serializers


from .models import Table
from .validators import table_properties_schema


class TablePropertiesSerializer(serializers.Serializer):
    headerLevel = serializers.CharField(required=True)
    timezone = serializers.CharField(required=True)
    language = serializers.CharField(required=True)
    trimWhitespaces = serializers.BooleanField(required=True)
    treatTheseAsNa = serializers.CharField(required=True, allow_blank=True)

    def validate(self, data):
        if not data:
            return data
        try:
            validate(data, table_properties_schema)
        except JSONValidationError as e:
            msg = e.message[:200] + "..." if len(e.message) > 200 else e.message
            raise serializers.ValidationError(f"Invalid properties data: {msg}")
        return data


class TableUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    properties = TablePropertiesSerializer()

    class Meta:
        fields = "__all__"
        read_only_fields = ("status", "preview_data", "has_errored", "error", "dataset")
        model = Table
