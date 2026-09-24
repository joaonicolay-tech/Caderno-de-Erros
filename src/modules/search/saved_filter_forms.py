"""Forms para salvar e gerenciar filtros da listagem atual."""

from typing import Any

from django import forms


class AccessibleSavedFilterForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                field.widget.attrs.setdefault("aria-describedby", f"id_{name}-help")


class SavedFilterCreateForm(AccessibleSavedFilterForm):
    name = forms.CharField(label="Nome do filtro", max_length=80)
    payload = forms.JSONField(widget=forms.HiddenInput, max_length=4096)


class SavedFilterRenameForm(AccessibleSavedFilterForm):
    name = forms.CharField(label="Novo nome", max_length=80)


class SavedFilterDeleteForm(AccessibleSavedFilterForm):
    confirm = forms.BooleanField(
        label="Confirmo que desejo excluir este filtro salvo",
        required=True,
        error_messages={"required": "Confirme a exclusão para continuar."},
    )
