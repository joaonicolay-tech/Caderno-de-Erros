"""Rotas diretas da conclusão de Review da E3."""

from django.urls import path

from .views import complete, correct_diagnosis, queue, timeline

app_name = "reviews"
urlpatterns = [
    path("", queue, name="queue"),
    path("timeline/<uuid:question_id>/", timeline, name="timeline"),
    path("diagnoses/<uuid:attempt_id>/correct/", correct_diagnosis, name="correct-diagnosis"),
    path("<uuid:review_id>/", complete, name="complete"),
]
