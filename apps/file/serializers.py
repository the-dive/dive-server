from rest_framework import serializers

from apps.file.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"
        read_only_fields = ("created_by", "modified_by")

    def create(self, validated_data):
        print(self.context["request"].user)
        validated_data["created_by"] = self.context["request"].user
        validated_data["modified_by"] = self.context["request"].user
        return super().create(validated_data)
