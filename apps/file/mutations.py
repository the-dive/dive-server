import graphene
from graphene_file_upload.scalars import Upload

from utils.graphene.error_types import (
    mutation_is_not_valid,
    CustomErrorType,
)

from apps.file.schema import FileType
from apps.file.serializers import FileSerializer
from apps.file.enums import FileTypeEnum


class CreateFileInputType(graphene.InputObjectType):
    file_type = graphene.Field(FileTypeEnum, required=True)
    file = Upload(required=True)


class CreateFile(graphene.Mutation):
    class Arguments:
        data = CreateFileInputType(required=True)

    errors = graphene.List(graphene.NonNull(CustomErrorType))
    ok = graphene.Boolean()
    result = graphene.Field(FileType)

    @staticmethod
    def mutate(root, info, data):
        serializer = FileSerializer(
            data=data, context={"request": info.context.request}
        )
        if errors := mutation_is_not_valid(serializer):
            return CreateFile(errors=errors, ok=False)
        instance = serializer.save()
        return CreateFile(result=instance, errors=None, ok=True)


class Mutation:
    create_file = CreateFile.Field()
