from jsonschema import validate, ValidationError as JSONValidationError
from rest_framework import serializers


from .models import Table
from .validators import table_properties_schema


class TableUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    properties = serializers.JSONField(required=False)

    class Meta:
        fields = '__all__'
        read_only_fields = ('status', 'preview_data', 'has_errored', 'error', 'dataset')
        model = Table

    def validate_properties(self, value):
        try:
            validate(value, table_properties_schema)
        except JSONValidationError as e:
            msg = e.message[:200] + "..." if len(e.message) > 200 else e.message
            raise serializers.ValidationError(f"Invalid properties data: {msg}")
        return value
