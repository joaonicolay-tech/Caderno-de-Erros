"""Rotas raiz da fundação local."""

from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include("modules.operations.urls")),
    path("taxonomy/", include("modules.taxonomy.urls")),
    path("questions/", include("modules.questions.urls")),
    path("", include("modules.accounts.urls")),
]
