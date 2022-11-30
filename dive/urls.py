import json

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from graphene_file_upload.django import FileUploadGraphQLView
from utils.graphene.context import GQLContext
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns


class CustomGraphQLView(FileUploadGraphQLView):
    """Handles multipart/form-data content type in django views"""

    def get_context(self, request):
        return GQLContext(request)

    def parse_body(self, request):
        """
        Allow for variable batch
        https://github.com/graphql-python/graphene-django/issues/967#issuecomment-640480919
        :param request:
        :return:
        """
        try:
            body = request.body.decode("utf-8")
            request_json = json.loads(body)
            self.batch = isinstance(request_json, list)
        except:  # noqa: E722
            self.batch = False
        return super().parse_body(request)


CustomGraphQLView.graphiql_template = "graphene_graphiql_explorer/graphiql.html"

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
)

urlpatterns += [
    path("graphiql/", csrf_exempt(CustomGraphQLView.as_view(graphiql=True))),
    path("graphql/", csrf_exempt(CustomGraphQLView.as_view())),
]

# Static and media file urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = _("Dive administration")
