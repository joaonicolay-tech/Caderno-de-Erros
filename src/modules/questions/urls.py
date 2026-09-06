"""Rotas do fluxo autorizado de cadastro de questões."""

from django.urls import path

from . import views

app_name = "questions"

urlpatterns = [
    path("new/", views.quick_entry, name="quick-entry"),
    path("drafts/<uuid:question_id>/activate/", views.draft_activate, name="draft-activate"),
]
