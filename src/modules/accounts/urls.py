"""Rotas da interface mínima do espaço local."""

from django.urls import path

from .views import home, initial_setup, priority, settings_view

app_name = "accounts"

urlpatterns = [
    path("", home, name="home"),
    path("prioridades/", priority, name="priority"),
    path("primeiro-acesso/", initial_setup, name="initial-setup"),
    path("configuracoes/", settings_view, name="settings"),
]
