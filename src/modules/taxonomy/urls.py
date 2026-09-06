"""Rotas da gestão web da taxonomia."""

from django.urls import path

from . import views

app_name = "taxonomy"

urlpatterns = [
    path("", views.taxonomy_index, name="index"),
    path("disciplines/new/", views.discipline_create, name="discipline-create"),
    path(
        "disciplines/<uuid:discipline_id>/edit/",
        views.discipline_edit,
        name="discipline-edit",
    ),
    path(
        "disciplines/<uuid:discipline_id>/archive/",
        views.discipline_archive,
        name="discipline-archive",
    ),
    path(
        "disciplines/<uuid:discipline_id>/subjects/",
        views.subject_list,
        name="subject-list",
    ),
    path(
        "disciplines/<uuid:discipline_id>/subjects/new/",
        views.subject_create,
        name="subject-create",
    ),
    path("subjects/<uuid:subject_id>/edit/", views.subject_edit, name="subject-edit"),
    path(
        "subjects/<uuid:subject_id>/archive/",
        views.subject_archive,
        name="subject-archive",
    ),
    path(
        "subjects/<uuid:subject_id>/subsubjects/",
        views.subsubject_list,
        name="subsubject-list",
    ),
    path(
        "subjects/<uuid:subject_id>/subsubjects/new/",
        views.subsubject_create,
        name="subsubject-create",
    ),
    path(
        "subsubjects/<uuid:subsubject_id>/edit/",
        views.subsubject_edit,
        name="subsubject-edit",
    ),
    path(
        "subsubjects/<uuid:subsubject_id>/archive/",
        views.subsubject_archive,
        name="subsubject-archive",
    ),
]
