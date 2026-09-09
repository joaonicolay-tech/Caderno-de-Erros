"""Entradas fechadas: resultado e Workspace nunca são aceitos do formulário."""

from typing import Any

from django import forms
from django.http import QueryDict

from modules.errors.models import ErrorCategory


class StrictForm(forms.Form):
    """Recuse campos inesperados e parâmetros repetidos, sem ecoar valores."""

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean() or {}
        allowed = {*self.fields, "csrfmiddlewaretoken", "action"}
        if set(self.data) - allowed or (
            isinstance(self.data, QueryDict)
            and any(len(self.data.getlist(key)) != 1 for key in self.data)
        ):
            raise forms.ValidationError("Solicitação inválida. Recarregue a página.")
        return cleaned


class AnswerForm(StrictForm):
    """Identificadores apresentados são revalidados pelo serviço."""

    revision_id = forms.UUIDField(widget=forms.HiddenInput)
    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    alternative_id = forms.ChoiceField(label="Sua resposta", widget=forms.RadioSelect)


class ConfirmationForm(StrictForm):
    """Diagnóstico mínimo opcional somente no formulário de erro."""

    token = forms.CharField(max_length=128, widget=forms.HiddenInput)
    key = forms.UUIDField(widget=forms.HiddenInput)
    category_id = forms.ModelChoiceField(
        label="Categoria principal do erro", queryset=ErrorCategory.objects.none(), required=False
    )
    other_description = forms.CharField(
        label="Descrição (obrigatória para Outra)",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class CancelForm(StrictForm):
    token = forms.CharField(max_length=128, widget=forms.HiddenInput)
