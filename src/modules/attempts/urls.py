"""Rotas somente da tentativa inicial E2."""

from django.urls import path

from .views import correction_preview, initial, replace_attempt, void_attempt

app_name = "attempts"
urlpatterns = [
    path("<uuid:question_id>/", initial, name="initial"),
    path("corrections/<uuid:attempt_id>/", correction_preview, name="correction-preview"),
    path("corrections/<uuid:attempt_id>/void/", void_attempt, name="void"),
    path("corrections/<uuid:attempt_id>/replace/", replace_attempt, name="replace"),
]
