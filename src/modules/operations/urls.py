"""Rotas operacionais estritamente locais."""

from django.urls import path

from .health import health

app_name = "operations"

urlpatterns = [path("health/", health, name="health")]
