"""Forms explícitos dos fluxos S2B de anulação e substituição."""

import uuid
from typing import Any, cast

from django import forms

from modules.questions.models import Alternative

_VOID_REASONS = (
    ("EVENT_DID_NOT_OCCUR", "O evento não ocorreu"),
    ("DUPLICATE_EVENT", "Registro duplicado"),
)
_REPLACEMENT_REASONS = (
    ("ANSWER_RECORDED_INCORRECTLY", "A resposta foi registrada incorretamente"),
    ("CONTEXT_RECORDED_INCORRECTLY", "O contexto foi registrado incorretamente"),
)


class AccessibleCorrectionForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                field.widget.attrs.setdefault("aria-describedby", f"id_{name}-help")


class AttemptVoidForm(AccessibleCorrectionForm):
    expected_tip_id = forms.UUIDField(widget=forms.HiddenInput)
    correlation_id = forms.UUIDField(widget=forms.HiddenInput)
    reason_code = forms.ChoiceField(label="Motivo da anulação", choices=_VOID_REASONS)
    confirm = forms.BooleanField(
        label="Confirmo que este evento não deveria permanecer como fato válido",
        required=True,
        error_messages={"required": "Confirme a anulação para continuar."},
    )


class AttemptReplacementForm(AccessibleCorrectionForm):
    expected_tip_id = forms.UUIDField(widget=forms.HiddenInput)
    correlation_id = forms.UUIDField(widget=forms.HiddenInput)
    idempotency_key = forms.UUIDField(widget=forms.HiddenInput)
    selected_alternative = forms.ModelChoiceField(
        label="Resposta registrada corretamente",
        queryset=Alternative.objects.none(),
    )
    perceived_ease = forms.ChoiceField(
        label="Facilidade percebida (opcional)",
        choices=(
            ("", "Não informar"),
            ("EASY", "Fácil"),
            ("MEDIUM", "Média"),
            ("HARD", "Difícil"),
        ),
        required=False,
    )
    reason_code = forms.ChoiceField(label="Motivo da substituição", choices=_REPLACEMENT_REASONS)
    confirm = forms.BooleanField(
        label="Confirmo a criação de uma nova Attempt e a anulação da atual",
        required=True,
        error_messages={"required": "Confirme a substituição para continuar."},
    )

    def __init__(
        self,
        *args: Any,
        workspace_id: uuid.UUID,
        revision_id: uuid.UUID,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        alternative_field = cast(
            "forms.ModelChoiceField[Alternative]", self.fields["selected_alternative"]
        )
        alternative_field.queryset = Alternative.objects.filter(
            workspace_id=workspace_id,
            question_revision_id=revision_id,
        ).order_by("position", "id")
