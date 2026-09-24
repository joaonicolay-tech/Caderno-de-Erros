"""Forms estruturais para operações S2A de Reviews."""

from typing import Any

from django import forms

_SCHEDULE_REASONS = (
    ("SCHEDULE_ADJUSTMENT", "Ajuste de agenda"),
    ("PERSONAL_COMMITMENT", "Compromisso pessoal"),
    ("OTHER_SCHEDULE_NEED", "Outra necessidade de agenda"),
)


class AccessibleReviewManagementForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                field.widget.attrs.setdefault("aria-describedby", f"id_{name}-help")


class ReviewRescheduleForm(AccessibleReviewManagementForm):
    expected_lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    new_due_date = forms.DateField(
        label="Nova data de revisão",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    reason_code = forms.ChoiceField(label="Motivo", choices=_SCHEDULE_REASONS)


class ManualReviewInclusionForm(AccessibleReviewManagementForm):
    reason_code = forms.ChoiceField(
        label="Motivo (opcional)",
        choices=[("", "Não informar"), ("MANUAL_REVIEW_REQUESTED", "Revisão solicitada")],
        required=False,
    )
    confirm = forms.BooleanField(
        label="Confirmo a inclusão de uma nova D1 manual",
        required=True,
        error_messages={"required": "Confirme a inclusão para continuar."},
    )
