"""Development não é um perfil de execução da rota Local r1."""

from django.core.exceptions import ImproperlyConfigured

raise ImproperlyConfigured("Use production_local para uso ou test para validação sintética.")
