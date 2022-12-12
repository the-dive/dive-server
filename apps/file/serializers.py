from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.file.models import File
from utils.common import get_file_extension

from dive.consts import MAX_FILE_SIZE_BYTES

EXTENSION_FILETYPE_MAP = {
    "xlsx": File.Type.EXCEL,
    "csv": File.Type.CSV,
    "json": File.Type.JSON,
    "txt": File.Type.TEXT,
}


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "file",
            "file_type",
        )
        read_only_fields = ("created_by", "modified_by", "file_size", "file_type")

    def validate_file(self, file):
        if file.size > MAX_FILE_SIZE_BYTES:
            raise ValidationError(
                f"File size should be less than {MAX_FILE_SIZE_BYTES}"
            )
        extension = get_file_extension(file.name)
        file_type = EXTENSION_FILETYPE_MAP.get(extension)
        if file_type is None:
            allowed = EXTENSION_FILETYPE_MAP.values()
            raise ValidationError(
                f"Invalid file type. Allowed types are {allowed}. Received '{extension}'"
            )
        return file

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        validated_data["modified_by"] = self.context["request"].user
        # get the file and calculate the file size
        file = validated_data["file"]
        validated_data["file_size"] = file.size
        extension = get_file_extension(file.name)
        validated_data["file_type"] = EXTENSION_FILETYPE_MAP[extension]
        return super().create(validated_data)
