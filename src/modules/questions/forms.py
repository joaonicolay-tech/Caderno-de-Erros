"""Forms de entrada do cadastro rápido, sem replicar regras do agregado."""

from __future__ import annotations

from typing import Any, cast

from django import forms

from modules.taxonomy.models import Discipline, Subject, Subsubject
from modules.taxonomy.selectors import (
    list_available_subjects,
    list_available_subsubjects,
    list_disciplines,
)

from .models import Board, Exam, QuestionDifficulty, Source, SourceType
from .selectors import list_boards, list_exams, list_sources
from .services import AlternativeInput, QuestionOriginInput
from .validators import (
    ALTERNATIVE_TEXT_MAX_LENGTH,
    QUESTION_DRAFT_TITLE_MAX_LENGTH,
    QUESTION_EXPLANATION_MAX_LENGTH,
    QUESTION_NOTES_MAX_LENGTH,
    QUESTION_REFERENCE_MAX_LENGTH,
    QUESTION_STEM_MAX_LENGTH,
    QUESTION_TRAP_NOTE_MAX_LENGTH,
)


class QuestionQuickEntryForm(forms.Form):
    """Colete valores e escolhas scoped; o serviço continua autoritativo."""

    draft_title = forms.CharField(
        label="Título provisório",
        max_length=QUESTION_DRAFT_TITLE_MAX_LENGTH,
        required=False,
        strip=False,
        help_text="Opcional para ativação; necessário no rascunho sem conteúdo.",
    )
    discipline: forms.ModelChoiceField[Discipline] = forms.ModelChoiceField(
        label="Disciplina",
        queryset=None,
        required=False,
        empty_label="Selecione uma disciplina",
    )
    subject: forms.ModelChoiceField[Subject] = forms.ModelChoiceField(
        label="Assunto",
        queryset=None,
        required=False,
        empty_label="Selecione um assunto",
    )
    subsubject: forms.ModelChoiceField[Subsubject] = forms.ModelChoiceField(
        label="Subassunto",
        queryset=None,
        required=False,
        empty_label="Sem subassunto",
    )
    difficulty = forms.ChoiceField(
        label="Dificuldade",
        choices=[("", "Não informar"), *QuestionDifficulty.choices],
        required=False,
    )
    stem = forms.CharField(
        label="Enunciado",
        max_length=QUESTION_STEM_MAX_LENGTH,
        required=False,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    alternative_1 = forms.CharField(
        label="Alternativa A", max_length=ALTERNATIVE_TEXT_MAX_LENGTH, required=False, strip=False
    )
    alternative_2 = forms.CharField(
        label="Alternativa B", max_length=ALTERNATIVE_TEXT_MAX_LENGTH, required=False, strip=False
    )
    alternative_3 = forms.CharField(
        label="Alternativa C", max_length=ALTERNATIVE_TEXT_MAX_LENGTH, required=False, strip=False
    )
    alternative_4 = forms.CharField(
        label="Alternativa D", max_length=ALTERNATIVE_TEXT_MAX_LENGTH, required=False, strip=False
    )
    correct_alternative = forms.ChoiceField(
        label="Gabarito",
        choices=[
            ("", "Selecione o gabarito"),
            ("1", "Alternativa A"),
            ("2", "Alternativa B"),
            ("3", "Alternativa C"),
            ("4", "Alternativa D"),
        ],
        required=False,
    )
    explanation = forms.CharField(
        label="Explicação",
        max_length=QUESTION_EXPLANATION_MAX_LENGTH,
        required=False,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    trap_note = forms.CharField(
        label="Pegadinha",
        max_length=QUESTION_TRAP_NOTE_MAX_LENGTH,
        required=False,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    notes = forms.CharField(
        label="Observações",
        max_length=QUESTION_NOTES_MAX_LENGTH,
        required=False,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    source: forms.ModelChoiceField[Source] = forms.ModelChoiceField(
        label="Fonte existente", queryset=None, required=False, empty_label="Nenhuma"
    )
    source_name = forms.CharField(label="Nova fonte", max_length=120, required=False, strip=False)
    source_type = forms.ChoiceField(
        label="Tipo da nova fonte",
        choices=[("", "Selecione o tipo"), *SourceType.choices],
        required=False,
    )
    source_url = forms.URLField(
        label="Endereço da nova fonte", max_length=2048, required=False, assume_scheme="https"
    )
    source_notes = forms.CharField(
        label="Observações da nova fonte",
        required=False,
        strip=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    exam: forms.ModelChoiceField[Exam] = forms.ModelChoiceField(
        label="Prova existente", queryset=None, required=False, empty_label="Nenhuma"
    )
    exam_name = forms.CharField(
        label="Nova prova ou concurso", max_length=120, required=False, strip=False
    )
    exam_year = forms.IntegerField(label="Ano da nova prova", required=False, min_value=1900)
    board: forms.ModelChoiceField[Board] = forms.ModelChoiceField(
        label="Banca existente", queryset=None, required=False, empty_label="Nenhuma"
    )
    board_name = forms.CharField(label="Nova banca", max_length=120, required=False, strip=False)
    board_website_url = forms.URLField(
        label="Site da nova banca", max_length=2048, required=False, assume_scheme="https"
    )
    reference_year = forms.IntegerField(label="Ano de referência", required=False, min_value=1900)
    reference_text = forms.CharField(
        label="Referência textual",
        max_length=QUESTION_REFERENCE_MAX_LENGTH,
        required=False,
        strip=False,
    )

    def __init__(self, *args: Any, workspace_id: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cast(
            "forms.ModelChoiceField[Discipline]", self.fields["discipline"]
        ).queryset = list_disciplines(workspace_id=workspace_id)
        cast(
            "forms.ModelChoiceField[Subject]", self.fields["subject"]
        ).queryset = list_available_subjects(workspace_id=workspace_id)
        cast(
            "forms.ModelChoiceField[Subsubject]", self.fields["subsubject"]
        ).queryset = list_available_subsubjects(workspace_id=workspace_id)
        cast("forms.ModelChoiceField[Source]", self.fields["source"]).queryset = list_sources(
            workspace_id=workspace_id
        )
        cast("forms.ModelChoiceField[Exam]", self.fields["exam"]).queryset = list_exams(
            workspace_id=workspace_id
        )
        cast("forms.ModelChoiceField[Board]", self.fields["board"]).queryset = list_boards(
            workspace_id=workspace_id
        )
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            field.widget.attrs["aria-describedby"] = f"{name}-help {name}-errors"

    def full_clean(self) -> None:
        super().full_clean()
        for name in self.errors:
            self.fields[name].widget.attrs["aria-invalid"] = "true"
        if self.errors:
            first = next(iter(self.errors))
            self.fields[first].widget.attrs["autofocus"] = True

    def alternative_inputs(self) -> tuple[list[AlternativeInput], int | None]:
        """Converta as quatro posições exibidas preservando sua ordem relativa."""
        values: list[AlternativeInput] = []
        correct_position: int | None = None
        selected = self.cleaned_data["correct_alternative"]
        for index in range(1, 5):
            value = self.cleaned_data[f"alternative_{index}"]
            if value and value.strip():
                values.append(AlternativeInput(text=value, label=chr(64 + index)))
                if selected == str(index):
                    correct_position = len(values)
        return values, correct_position

    def origin_input(self) -> QuestionOriginInput:
        """Monte a entrada opcional; criação/reuso e invariantes ficam no serviço."""
        return QuestionOriginInput(
            source_id=self.cleaned_data["source"].id if self.cleaned_data["source"] else None,
            source_name=self.cleaned_data["source_name"],
            source_type=self.cleaned_data["source_type"] or None,
            source_url=self.cleaned_data["source_url"],
            source_notes=self.cleaned_data["source_notes"],
            exam_id=self.cleaned_data["exam"].id if self.cleaned_data["exam"] else None,
            exam_name=self.cleaned_data["exam_name"],
            exam_year=self.cleaned_data["exam_year"],
            board_id=self.cleaned_data["board"].id if self.cleaned_data["board"] else None,
            board_name=self.cleaned_data["board_name"],
            board_website_url=self.cleaned_data["board_website_url"],
            reference_year=self.cleaned_data["reference_year"],
            reference_text=self.cleaned_data["reference_text"],
        )


class DraftActivationForm(QuestionQuickEntryForm):
    """Inclua a versão observada para impedir sobrescrita perdida ao ativar."""

    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


class QuestionEditForm(QuestionQuickEntryForm):
    """Edite o agregado observado sem permitir sobrescrita concorrente."""

    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)


class QuestionArchiveForm(forms.Form):
    """Exija confirmação explícita sobre a versão observada da questão."""

    lock_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    confirm = forms.BooleanField(
        label="Confirmo que desejo arquivar esta questão",
        required=True,
        error_messages={"required": "Confirme o arquivamento para continuar."},
    )

    def full_clean(self) -> None:
        super().full_clean()
        if "confirm" in self.errors:
            self.fields["confirm"].widget.attrs.update(
                {
                    "aria-invalid": "true",
                    "aria-describedby": "confirm-help confirm-errors",
                    "autofocus": True,
                }
            )
