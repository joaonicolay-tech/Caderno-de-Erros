"""Formulário estrito da correção auditável E4."""

from typing import Any, cast

from django import forms

from .models import ErrorCategory


class ErrorClassificationCorrectionForm(forms.Form):
    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    category = forms.ModelChoiceField(
        label="Categoria corrigida", queryset=ErrorCategory.objects.none()
    )
    other_description = forms.CharField(
        label="Descrição para Outra",
        required=False,
        max_length=500,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    change_reason = forms.CharField(
        label="Razão da correção",
        required=False,
        max_length=1000,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args: Any, workspace_id: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        field = cast("forms.ModelChoiceField[ErrorCategory]", self.fields["category"])
        field.queryset = ErrorCategory.objects.filter(workspace_id=workspace_id)
