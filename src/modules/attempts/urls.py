"""Rotas somente da tentativa inicial E2."""

from django.urls import path

from .views import initial

app_name = "attempts"
urlpatterns = [path("<uuid:question_id>/", initial, name="initial")]
