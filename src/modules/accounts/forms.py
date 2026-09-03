"""Formulários superficiais da configuração local da V0.1."""

from typing import Any
from zoneinfo import available_timezones

from django import forms

from shared.domain.time import TimeZoneId

TIMEZONE_CHOICES = (
    ("", "Selecione um fuso horário"),
    *((name, name) for name in sorted(available_timezones())),
)


class TimezoneFormMixin(forms.Form):
    """Compartilhe a entrada IANA sem duplicar a regra do domínio."""

    timezone_name = forms.ChoiceField(
        label="Fuso horário",
        choices=TIMEZONE_CHOICES,
        help_text="Escolha um identificador IANA, por exemplo America/Sao_Paulo.",
        error_messages={
            "required": "Escolha um fuso horário.",
            "invalid_choice": "Escolha um identificador de fuso IANA válido.",
        },
    )

    def clean_timezone_name(self) -> str:
        """Normalize pelo mesmo objeto de valor usado nos serviços."""
        value = self.cleaned_data["timezone_name"]
        if not isinstance(value, str):
            raise forms.ValidationError("Escolha um identificador de fuso IANA válido.")
        try:
            return TimeZoneId(value).value
        except ValueError as error:
            raise forms.ValidationError(
                "Escolha um identificador de fuso IANA válido.",
                code="invalid_timezone",
            ) from error

    def mark_accessibility_state(self) -> None:
        """Associe ajuda/erro e leve o foco ao primeiro campo inválido."""
        field = self.fields["timezone_name"]
        field.widget.attrs["aria-describedby"] = "timezone-help timezone-errors"
        field.widget.attrs["aria-required"] = "true"
        if "timezone_name" in self.errors:
            field.widget.attrs["aria-invalid"] = "true"
            field.widget.attrs["autofocus"] = True


class InitialSetupForm(TimezoneFormMixin):
    """Escolha explícita de fuso no primeiro acesso."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.mark_accessibility_state()


class TimezoneChangeForm(TimezoneFormMixin):
    """Mudança confirmada e protegida pela versão apresentada."""

    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    confirmed = forms.BooleanField(
        label="Confirmo a alteração do fuso horário",
        error_messages={"required": "Confirme a alteração antes de salvar."},
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        confirmed = self.fields["confirmed"]
        confirmed.widget.attrs["aria-describedby"] = "timezone-impact confirmed-errors"
        if "confirmed" in self.errors:
            confirmed.widget.attrs["aria-invalid"] = "true"
            confirmed.widget.attrs["autofocus"] = True
        self.mark_accessibility_state()
