from rest_framework import serializers

from apps.file.models import File
from apps.file.utils import create_dataset_table


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "file",
            "file_type",
        )
        read_only_fields = ("created_by", "modified_by", "file_size")

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        validated_data["modified_by"] = self.context["request"].user
        # get the file and calulate the file size
        file = validated_data["file"]
        validated_data["file_size"] = file.size
        file = super().create(validated_data)
        if file:
            create_dataset_table(file)
        return file
