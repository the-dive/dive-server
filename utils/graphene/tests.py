import os
import json
import shutil
import datetime
from enum import Enum

from django.utils import timezone
from django.conf import settings


from graphene_django.utils import GraphQLTestCase as BaseGraphQLTestCase
from rest_framework import status


TEST_MEDIA_ROOT = "media-temp"


class CommonSetupClassMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # add necessary stuffs

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # clear the temporary media files
        try:
            shutil.rmtree(
                os.path.join(settings.BASE_DIR, TEST_MEDIA_ROOT), ignore_errors=True
            )
        except FileNotFoundError:
            pass


class GraphQLTestCase(CommonSetupClassMixin, BaseGraphQLTestCase):
    """
    GraphQLTestCase with custom helper methods
    """

    GRAPHQL_SCHEMA = "dive.schema.graphql"
    ENABLE_NOW_PATCHER = False

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def force_login(self, user):
        self.client.force_login(user)

    def genum(self, _enum: Enum):
        """
        Return appropriate enum value.
        """
        return _enum.name

    def assertResponseErrors(self, resp, msg=None):
        """
        Assert that the call went through correctly but with error. 200 means the syntax is ok,
        if there are `errors`, the call wasn't fine.
        :resp HttpResponse: Response
        """
        content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200, msg or content)
        self.assertIn("errors", list(content.keys()), msg or content)

    def query_check(
        self,
        query,
        minput=None,
        mnested=None,
        assert_for_error=False,
        okay=None,
        **kwargs,
    ) -> dict:
        if minput:
            response = self.query(query, input_data=minput, **kwargs)
        else:
            response = self.query(query, **kwargs)
        content = response.json()
        if assert_for_error:
            self.assertResponseErrors(response)
        else:
            self.assertResponseNoErrors(response)
            if okay is not None:
                _content = content["data"]
                if mnested:
                    for key in mnested:
                        _content = _content[key]
                for key, datum in _content.items():
                    if key == "__typename":
                        continue
                    okay_response = datum.get("ok")
                    if okay:
                        self.assertTrue(okay_response, content)
                    else:
                        self.assertFalse(okay_response, content)
        return content

    def assertListIds(
        self,
        current_list,
        excepted_list,
        message=None,
        get_current_list_id=lambda x: str(x["id"]),
        get_excepted_list_id=lambda x: str(x.id),
    ):
        self.assertEqual(
            set([get_current_list_id(item) for item in current_list]),
            set([get_excepted_list_id(item) for item in excepted_list]),
            message,
        )

    def assertNotListIds(
        self,
        current_list,
        excepted_list,
        message=None,
        get_current_list_id=lambda x: str(x["id"]),
        get_not_excepted_list_id=lambda x: str(x.id),
    ):
        self.assertNotEqual(
            set([get_current_list_id(item) for item in current_list]),
            set([get_not_excepted_list_id(item) for item in excepted_list]),
            message,
        )

    def assertIdEqual(self, excepted, real, message=None):
        return self.assertEqual(str(excepted), str(real), message)

    def assertCustomDictEqual(
        self, excepted, real, message=None, ignore_keys=[], only_keys=[]
    ):
        def _filter_by_keys(_dict, keys, exclude=False):
            def _include(key):
                if exclude:
                    return key not in keys
                return key in keys

            return {key: value for key, value in _dict.items() if _include(key)}

        if only_keys:
            assert _filter_by_keys(excepted, keys=only_keys) == _filter_by_keys(
                real, keys=only_keys
            ), message
        elif ignore_keys:
            assert _filter_by_keys(
                excepted, keys=ignore_keys, exclude=True
            ) == _filter_by_keys(real, keys=ignore_keys, exclude=True), message
        else:
            assert excepted == real, message

    def assertQuerySetIdEqual(self, l1, l2):
        return self.assertEqual(
            sorted([each.id for each in l1]),
            sorted([each.id for each in l2]),
        )

    def get_media_url(self, file):
        return f"http://testserver/media/{file}"

    def update_obj(self, obj, **fields):
        for key, value in fields.items():
            setattr(obj, key, value)
        obj.save()
        return obj

    def get_datetime_str(self, datetime):
        return datetime.strftime("%Y-%m-%d%z")

    def get_date_str(self, datetime):
        return datetime.strftime("%Y-%m-%d")

    def get_aware_datetime(self, *args, **kwargs):
        return timezone.make_aware(datetime.datetime(*args, **kwargs))

    def get_aware_datetime_str(self, *args, **kwargs):
        return self.get_datetime_str(self.get_aware_datetime(*args, **kwargs))

    # Some Rest helper functions
    def assert_http_code(self, response, status_code):
        error_resp = getattr(response, "data", None)
        mesg = error_resp
        if type(error_resp) is dict and "errors" in error_resp:
            mesg = error_resp["errors"]
        return self.assertEqual(response.status_code, status_code, mesg)

    def assert_403(self, response):
        self.assert_http_code(response, status.HTTP_403_FORBIDDEN)

    def assert_200(self, response):
        self.assert_http_code(response, status.HTTP_200_OK)
