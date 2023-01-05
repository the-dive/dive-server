import os
from django.core.files.base import File as File_

from apps.core.models import File


def create_test_file(file_path: str, file_name="test.xlsx") -> File:
    test_file = open(file_path, "rb")
    return File.objects.create(
        file_type=File.Type.EXCEL,
        # NOTE: if the name argument is not passed in the following line,
        # SuspiciousFileOperation will be raised by django as the file name
        # will be /some/absolute/path.xlsx
        file=File_(test_file, name=file_name),
        file_size=os.path.getsize(file_path),
    )
