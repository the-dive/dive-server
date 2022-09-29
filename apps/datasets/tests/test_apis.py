from dive.base_test import BaseAPITestCase


class TestAPIs(BaseAPITestCase):
    def test_example(self):
        user = self.create_dummy_user()
        print(user)
