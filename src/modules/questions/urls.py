"""Rotas do fluxo autorizado de cadastro de questões."""

from django.urls import path

from . import views

app_name = "questions"

urlpatterns = [
    path("new/", views.quick_entry, name="quick-entry"),
    path("drafts/<uuid:question_id>/activate/", views.draft_activate, name="draft-activate"),
    path("<uuid:question_id>/", views.question_detail, name="detail"),
    path("<uuid:question_id>/edit/", views.question_edit, name="edit"),
    path("<uuid:question_id>/archive/", views.question_archive, name="archive"),
]
