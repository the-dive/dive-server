import graphene
from graphene_django import DjangoObjectType
from graphene_django_extras import PageGraphqlPagination, DjangoObjectField

from utils.graphene.types import CustomDjangoListObjectType
from utils.graphene.fields import DjangoPaginatedListObjectField

from apps.file.models import File
from apps.file.filter_set import FileFilterSet


class FileType(DjangoObjectType):
    class Meta:
        model = File
        fields = (
            "id",
            "file",
            "file_type",
        )


class FileDetailType(
    # -- Start File Scopped Entities
    # -- End File Scopped Entities
    FileType
):
    class Meta:
        model = File
        skip_registry = True
        fields = "__all__"


class FileListType(CustomDjangoListObjectType):
    class Meta:
        model = File
        filterset_class = FileFilterSet


class Query(graphene.ObjectType):
    file = DjangoObjectField(FileDetailType)
    files = DjangoPaginatedListObjectField(
        FileListType, pagination=PageGraphqlPagination(page_size_query_param="pageSize")
    )
