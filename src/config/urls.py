"""Rotas raiz da fundação local."""

from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include("modules.operations.urls")),
    path("categories/", include("modules.errors.urls")),
    path("taxonomy/", include("modules.taxonomy.urls")),
    path("questions/filters/", include("modules.search.urls")),
    path("questions/", include("modules.questions.urls")),
    path("initial/", include("modules.attempts.urls")),
    path("reviews/", include("modules.reviews.urls")),
    path("", include("modules.accounts.urls")),
]
