"""
URL configuration for neshaa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpResponseNotFound
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from django.views.generic import RedirectView

from commons.views_readiness import readiness_probe


def block_other_urls(request, *args, **kwargs):
    return HttpResponseNotFound("Not Found")


urlpatterns = [
    path("ndash", admin.site.urls),
    path("readiness", readiness_probe, name="readiness-probe"),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico', permanent=True)),
    path("", block_other_urls),  # Block root
    path("<path:resource>", block_other_urls),  # Block all other URLs
]
