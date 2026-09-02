"""Rotas raiz; capacidades web serão adicionadas somente em suas etapas."""

from django.urls.resolvers import URLPattern, URLResolver

urlpatterns: list[URLPattern | URLResolver] = []
