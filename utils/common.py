import os

from django.db import models
from django.utils.translation import gettext_lazy as _


class ColumnTypes(models.TextChoices):
    STRING = "string", _("String")
    NUMBER = "number", _("Number")
    INTEGER = "integer", _("Integer")
    FLOAT = "float", _("Float")
    DATE = "date", _("Date")
    TIME = "time", _("Time")
    DATETIME = "datetime", _("Date time")
    LOCATION = "location", _("Location")


def to_camelcase(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def get_file_extension(file_path: str):
    return os.path.splitext(file_path)[1].replace(".", "")
