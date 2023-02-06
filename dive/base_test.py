import os
import pandas as pd

from apps.core.models import File
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.base import File as File_
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient  # type: ignore

from utils.helpers import generate_random_key
from apps.core.validators import get_default_table_properties
from apps.core.utils import create_dataset_and_tables

User = get_user_model()

TEST_MEDIA_DIR = os.path.join(settings.TEST_DIR, "media")
TEST_FILE_PATH = os.path.join(settings.TEST_DIR, "documents", "test1.xlsx")


class BaseAPITestCase(APITestCase):
    """Base testcase that handles authentication"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = APIClient()
        self.password = "testing"
        self.username = "testuser"

    @staticmethod
    def create_dummy_user(first_name=None, email=None):
        user = User.objects.create(
            first_name=(first_name or "Test-" + generate_random_key(5)),
            username=generate_random_key(5),
            last_name="User",
            email=(email or generate_random_key(5) + "@test.com"),
            is_superuser=False,
        )
        return user

    def setUp(self):
        self.user = User.objects.create(
            first_name="Test",
            username=self.username,
            last_name="User",
            email="user@test.com",
            is_superuser=False,
        )
        self.user.set_password(self.password)
        self.user.save()

    def set_auth(self, user=None):
        return self.user if user is None else user

    def tearDown(self):
        try:
            # Logout if logged in. Assume try except handles if not logged in
            pass
        except Exception:
            pass


def assert_object_created(Model, count=1):
    """
    Decorator for test cases to assert <count> objects of type Model are created
    """

    def wrapper(function):
        def new_function(*args, **kwargs):
            initial_count = Model.objects.count()
            ret = function(*args, **kwargs)
            assert (
                Model.objects.count() == initial_count + count
            ), f"There must be {count} more {Model.__name__} created"  # noqa
            return ret

        return new_function

    return wrapper


NUM_ROWS = 10
DATA = {
    "id": [x for x in range(1, NUM_ROWS + 1)],
    "name": [
        "Sam",
        "Morgan",
        "Rishi",
        "Shreeyash",
        "Sameer",
        "Bibek",
        "",
        "Patrice",
        "Ram",
        "Sita",
    ],
    "income": [x * 2000 for x in range(1, NUM_ROWS + 1)],
}

DATAFRAME = pd.DataFrame(data=DATA)


class BaseTestWithDataFrameAndExcel(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_table_properties = get_default_table_properties()

    def setUp(self):
        self.excel_file_path = "test_result.xlsx"
        DATAFRAME.to_excel(self.excel_file_path, index=False)

        file_name = "test.xlsx"
        file_obj = create_test_file(self.excel_file_path, file_name=file_name)
        self.dataset = create_dataset_and_tables(file_obj)

    def tearDown(self):
        """Remove file path"""
        if os.path.exists(self.excel_file_path):
            os.remove(self.excel_file_path)


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
