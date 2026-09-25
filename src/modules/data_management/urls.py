"""Local data portability routes."""

from django.urls import path

from .views import portability

app_name = "data-management"

urlpatterns = [path("dados/", portability, name="portability")]
