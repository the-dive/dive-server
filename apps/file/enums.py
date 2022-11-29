from utils.graphene.enums import (
    convert_enum_to_graphene_enum,
    get_enum_name_from_django_field,
)

from apps.file.models import File

FileTypeEnum = convert_enum_to_graphene_enum(File.Type, name="FileTypeEnum")

enum_map = {
    get_enum_name_from_django_field(field): enum
    for field, enum in ((File.file_type, FileTypeEnum),)
}
