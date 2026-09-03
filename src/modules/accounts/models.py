"""Persistência de identidade e Workspace da V0.1."""

import uuid
from typing import Any, ClassVar

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q

from .validators import validate_iana_timezone


class UserStatus(models.TextChoices):
    """Estados persistidos da identidade."""

    ACTIVE = "ACTIVE", "Ativo"
    DISABLED = "DISABLED", "Desabilitado"


class UserManager(BaseUserManager["User"]):
    """Crie identidades usando o mecanismo de credenciais do Django."""

    use_in_migrations = True

    def create_user(
        self,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        normalized_email = self.normalize_email(email) if email else None
        user = self.model(email=normalized_email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Identidade autenticável com UUID desde a primeira migração."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        db_table = "accounts_user"
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=Q(status__in=UserStatus.values),
                name="accounts_user_status_valid",
            )
        ]

    @property
    def is_active(self) -> bool:
        """Traduza o estado de domínio para o contrato do backend Django."""
        return self.status == UserStatus.ACTIVE

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self.status = UserStatus.ACTIVE if value else UserStatus.DISABLED

    def __str__(self) -> str:
        return self.display_name or self.email or str(self.id)


class WorkspaceLocale(models.TextChoices):
    """Locales atualmente suportados pelo produto."""

    PT_BR = "pt-BR", "Português (Brasil)"


class Workspace(models.Model):
    """Fronteira obrigatória dos dados de um estudante."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="workspaces",
    )
    name = models.CharField(max_length=120)
    timezone_name = models.CharField(max_length=64, validators=[validate_iana_timezone])
    locale = models.CharField(
        max_length=16,
        choices=WorkspaceLocale.choices,
        default=WorkspaceLocale.PT_BR,
    )
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_workspace"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["owner_user"], name="workspace_owner_idx")
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="workspace_lock_positive",
            )
        ]

    def __str__(self) -> str:
        return self.name
