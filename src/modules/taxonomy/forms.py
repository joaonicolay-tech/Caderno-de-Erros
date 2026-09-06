"""Entrada acessível da gestão web de taxonomia."""

from typing import Any

from django import forms


class TaxonomyNameForm(forms.Form):
    """Colete nome sem duplicar a normalização do domínio."""

    name = forms.CharField(
        label="Nome",
        max_length=120,
        strip=False,
        help_text="Use um nome claro, com no máximo 120 caracteres.",
        error_messages={
            "required": "Informe o nome.",
            "max_length": "O nome deve ter no máximo 120 caracteres.",
        },
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["aria-describedby"] = "name-help name-errors"
        self.fields["name"].widget.attrs["aria-required"] = "true"
        if "name" in self.errors:
            self.focus_name_error()

    def focus_name_error(self) -> None:
        """Marque o campo para anunciar e receber foco após erro."""
        self.fields["name"].widget.attrs["aria-invalid"] = "true"
        self.fields["name"].widget.attrs["autofocus"] = True


class TaxonomyEditForm(TaxonomyNameForm):
    """Envie a versão vista junto da edição."""

    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


class TaxonomyArchiveForm(forms.Form):
    """Exija confirmação explícita e versão atual no arquivamento."""

    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    confirmed = forms.BooleanField(
        label="Confirmo que desejo arquivar este item",
        error_messages={"required": "Confirme o arquivamento antes de continuar."},
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        field = self.fields["confirmed"]
        field.widget.attrs["aria-describedby"] = "archive-impact confirmed-errors"
        if "confirmed" in self.errors:
            self.focus_confirmation_error()

    def focus_confirmation_error(self) -> None:
        """Marque a confirmação inválida para tecnologia assistiva."""
        field = self.fields["confirmed"]
        field.widget.attrs["aria-invalid"] = "true"
        field.widget.attrs["autofocus"] = True
