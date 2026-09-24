"""Rotas de gestão de categorias pessoais."""

from django.urls import path

from . import views

app_name = "categories"

urlpatterns = [
    path("", views.category_list, name="list"),
    path("new/", views.create_category, name="create"),
    path("<uuid:category_id>/rename/", views.rename_category, name="rename"),
    path("<uuid:category_id>/archive/", views.archive_category, name="archive"),
    path("<uuid:category_id>/merge/", views.merge_category, name="merge"),
]
