"""Forms explícitos das operações S2C e S2D expostas pela UI."""

from collections.abc import Iterable
from typing import Any, cast

from django import forms

from modules.questions.models import Alternative


class AccessibleManagementForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                field.widget.attrs.setdefault("aria-describedby", f"id_{name}-help")


class AnswerKeyCorrectionForm(AccessibleManagementForm):
    expected_revision_id = forms.UUIDField(widget=forms.HiddenInput)
    correct_alternative_position = forms.ChoiceField(label="Novo gabarito")
    reason_code = forms.ChoiceField(
        label="Motivo",
        choices=(
            ("ANSWER_KEY_PUBLISHED_INCORRECT", "O gabarito publicado estava incorreto"),
            (
                "CORRECT_OPTION_MISIDENTIFIED",
                "A alternativa correta foi identificada incorretamente",
            ),
        ),
    )
    confirm = forms.BooleanField(
        label="Confirmo que a correção vale para tentativas futuras",
        required=True,
        error_messages={"required": "Confirme a correção para continuar."},
    )

    def __init__(
        self,
        *args: Any,
        alternatives: Iterable[Alternative],
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        position_field = cast(forms.ChoiceField, self.fields["correct_alternative_position"])
        position_field.choices = [
            (str(item.position), f"Alternativa {item.label or item.position}: {item.text}")
            for item in alternatives
        ]


class PermanentQuestionDeleteForm(AccessibleManagementForm):
    expected_fingerprint = forms.CharField(widget=forms.HiddenInput)
    confirmation_token = forms.CharField(widget=forms.HiddenInput)
    correlation_id = forms.UUIDField(widget=forms.HiddenInput)
    confirmation_text = forms.CharField(label="Digite o código de confirmação")
    backup_acknowledgement = forms.BooleanField(
        label="Entendo que o backup será criado, validado e restaurado isoladamente antes da exclusão",
        required=False,
    )
    confirm = forms.BooleanField(
        label="Confirmo a exclusão permanente deste agregado",
        required=True,
        error_messages={"required": "Confirme a exclusão para continuar."},
    )

    def __init__(
        self,
        *args: Any,
        required_token: str,
        backup_required: bool,
        **kwargs: Any,
    ) -> None:
        self.required_token = required_token
        self.backup_required = backup_required
        super().__init__(*args, **kwargs)
        self.fields[
            "confirmation_text"
        ].help_text = f"Para confirmar, digite exatamente: {required_token}"
        if not backup_required:
            self.fields.pop("backup_acknowledgement")

    def clean_confirmation_text(self) -> str:
        value = cast(str, self.cleaned_data["confirmation_text"]).strip()
        if value != self.required_token:
            raise forms.ValidationError("O código digitado não corresponde ao preview atual.")
        return value

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        if cleaned is None:
            return {}
        if self.backup_required and not cleaned.get("backup_acknowledgement"):
            self.add_error(
                "backup_acknowledgement",
                "Reconheça o requisito de backup antes de confirmar.",
            )
        return cleaned
