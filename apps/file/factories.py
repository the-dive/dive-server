import factory
from factory import fuzzy

from apps.file.models import File
from dive.factories import BaseModelFactory


class FileFactory(BaseModelFactory):
    class Meta:
        model = File

    file = factory.django.FileField(filename="test.xlsx")
    file_type = fuzzy.FuzzyChoice(File.Type)
