"""Forms explícitos para lifecycle de categorias pessoais S2A."""

import uuid
from typing import Any, cast

from django import forms

from .models import ErrorCategory, ErrorCategoryKind, ErrorCategoryState

_CATEGORY_REASONS = (
    ("PERSONAL_ORGANIZATION", "Organização pessoal"),
    ("CATEGORY_MAINTENANCE", "Manutenção das categorias"),
    ("OTHER_CATEGORY_NEED", "Outra necessidade de organização"),
)


class AccessibleCategoryManagementForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                field.widget.attrs.setdefault("aria-describedby", f"id_{name}-help")


class PersonalCategoryCreateForm(AccessibleCategoryManagementForm):
    display_name = forms.CharField(label="Nome da categoria", max_length=120)


class PersonalCategoryRenameForm(AccessibleCategoryManagementForm):
    expected_lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    display_name = forms.CharField(label="Novo nome", max_length=120)
    reason_code = forms.ChoiceField(label="Motivo", choices=_CATEGORY_REASONS)


class PersonalCategoryArchiveForm(AccessibleCategoryManagementForm):
    expected_lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    reason_code = forms.ChoiceField(label="Motivo", choices=_CATEGORY_REASONS)
    confirm = forms.BooleanField(
        label="Confirmo o arquivamento desta categoria pessoal",
        required=True,
        error_messages={"required": "Confirme o arquivamento para continuar."},
    )


class PersonalCategoryMergeForm(AccessibleCategoryManagementForm):
    expected_lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    target = forms.ModelChoiceField(queryset=ErrorCategory.objects.none(), label="Categoria alvo")
    reason_code = forms.ChoiceField(label="Motivo", choices=_CATEGORY_REASONS)
    confirm = forms.BooleanField(
        label="Confirmo a consolidação da origem na categoria alvo",
        required=True,
        error_messages={"required": "Confirme a consolidação para continuar."},
    )

    def __init__(
        self,
        *args: Any,
        workspace_id: uuid.UUID,
        source_id: uuid.UUID,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        target_field = cast("forms.ModelChoiceField[ErrorCategory]", self.fields["target"])
        target_field.queryset = (
            ErrorCategory.objects.filter(
                workspace_id=workspace_id,
                category_kind=ErrorCategoryKind.PERSONAL,
                state=ErrorCategoryState.ACTIVE,
            )
            .exclude(pk=source_id)
            .order_by("display_name", "id")
        )
