"""Rotas de filtros salvos da listagem de Questions."""

from django.urls import path

from . import saved_filter_views

app_name = "search"

urlpatterns = [
    path("create/", saved_filter_views.create_filter, name="create-filter"),
    path("<uuid:saved_filter_id>/apply/", saved_filter_views.apply_filter, name="apply-filter"),
    path("<uuid:saved_filter_id>/rename/", saved_filter_views.rename_filter, name="rename-filter"),
    path("<uuid:saved_filter_id>/delete/", saved_filter_views.delete_filter, name="delete-filter"),
]
