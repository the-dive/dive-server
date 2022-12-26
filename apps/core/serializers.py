from rest_framework import serializers


from .models import Table


class TableUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        fields = '__all__'
        read_only_fields = ('status', 'preview_data', 'has_errored', 'error', 'dataset')
        model = Table
