from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient  # type: ignore

from utils.helpers import generate_random_key

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """Base testcase that handles authentication"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = APIClient()
        self.password = 'testing'
        self.username = 'testuser'

    @staticmethod
    def create_dummy_user(first_name=None, email=None):
        user = User.objects.create(
            first_name=(first_name or 'Test-' + generate_random_key(5)),
            username=generate_random_key(5),
            last_name='User',
            email=(email or generate_random_key(5) + '@test.com'),
            is_superuser=False
        )
        return user

    def setUp(self):
        self.user = User.objects.create(
            first_name='Test',
            username=self.username,
            last_name='User',
            email='user@test.com',
            is_superuser=False
        )
        self.user.set_password(self.password)
        self.user.save()

    def set_auth(self, user=None):
        # Do Login
        pass
        usr = self.user if user is None else user

    def tearDown(self):
        try:
            # Logout if logged in. Assume try except handles if not logged in
            pass
        except Exception:
            pass


def assert_count_increment(Model, increment_count=1):
    def wrapper(function):
        def new_function(*args, **kwargs):
            initial_count = Model.objects.count()
            ret = function(*args, **kwargs)
            assert Model.objects.count() == initial_count + increment_count, \
                f"There must be {increment_count} more {Model.__name__} created"  # noqa
            return ret
        return new_function
    return wrapper
