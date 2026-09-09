"""Rotas diretas da conclusão de Review da E3."""

from django.urls import path

from .views import complete

app_name = "reviews"
urlpatterns = [path("<uuid:review_id>/", complete, name="complete")]
