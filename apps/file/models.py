from django.db import models
from django.utils.translation import gettext_lazy as _

from dive.base_models import BaseModel


class File(BaseModel):
    class Type(models.TextChoices):
        EXCEL = "excel", _("Excel")
        CSV = "csv", _("Csv")
        JSON = "json", _("Json")
        TEXT = "text", _("Text")

    file_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name=_("File type"),
    )
    file = models.FileField(
        verbose_name=_("File"), max_length=255, upload_to="imported_files/"
    )
    file_size = models.PositiveIntegerField(
        verbose_name=_("File size"),
    )
