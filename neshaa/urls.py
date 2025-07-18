from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseNotFound
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

from commons.views import readiness_probe


def block_other_urls(request, *args, **kwargs):
    return HttpResponseNotFound("Not Found")


urlpatterns = [
    path("courses/", include("courses.urls")),
    path("financials/", include("financials.urls")),
    path("ndash/", admin.site.urls),
    path("readiness/", readiness_probe, name="readiness-probe"),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico", permanent=True)),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    path("", block_other_urls),
    path("<path:resource>", block_other_urls),
]

if settings.DEBUG and not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = debug_toolbar_urls() + urlpatterns
