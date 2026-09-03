"""Catálogo canônico aprovado por ERR-V01-009."""

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StandardErrorCategoryDefinition:
    """Texto atual associado a um código histórico estável."""

    code: str
    display_name: str
    description: str


def normalize_name_key(value: str) -> str:
    """Normalize espaços, Unicode e caixa sem remover acentos legítimos."""
    collapsed = " ".join(value.strip().split())
    return unicodedata.normalize("NFC", collapsed).casefold()


STANDARD_ERROR_CATEGORIES = (
    StandardErrorCategoryDefinition(
        "CONCEPTUAL",
        "Conceitual",
        "Erro causado por compreensão incorreta, incompleta ou ausente de um conceito "
        "necessário para resolver a questão.",
    ),
    StandardErrorCategoryDefinition(
        "INTERPRETATION",
        "Interpretação",
        "Erro causado pela compreensão incorreta do enunciado, texto, comando, gráfico, "
        "tabela ou informação apresentada.",
    ),
    StandardErrorCategoryDefinition(
        "CALCULATION",
        "Cálculo",
        "Erro causado durante a execução de operações matemáticas, algébricas ou numéricas, "
        "apesar de o método ou conceito estar correto.",
    ),
    StandardErrorCategoryDefinition(
        "ATTENTION",
        "Atenção",
        "Erro causado por distração, leitura apressada, troca de sinais, omissão de informação "
        "ou outro descuido de execução.",
    ),
    StandardErrorCategoryDefinition(
        "FORMULA_RULE",
        "Fórmula/regra",
        "Erro causado pelo desconhecimento, esquecimento ou aplicação incorreta de uma fórmula, "
        "regra, propriedade ou convenção.",
    ),
    StandardErrorCategoryDefinition(
        "PROCEDURE",
        "Procedimento",
        "Erro causado pela escolha, ordem ou execução inadequada das etapas necessárias para "
        "resolver a questão.",
    ),
    StandardErrorCategoryDefinition(
        "TRAP",
        "Pegadinha",
        "Erro provocado por alternativa, formulação ou detalhe do enunciado que induz a uma "
        "interpretação ou resposta aparentemente correta, mas inadequada.",
    ),
    StandardErrorCategoryDefinition(
        "TIME_SHORTAGE",
        "Falta de tempo",
        "Erro ou questão não concluída adequadamente porque o tempo disponível foi insuficiente "
        "para analisar ou resolver a questão.",
    ),
    StandardErrorCategoryDefinition(
        "GUESS",
        "Chute",
        "Resposta escolhida sem conhecimento ou justificativa suficiente, baseada "
        "predominantemente em tentativa ou acaso.",
    ),
    StandardErrorCategoryDefinition(
        "OTHER",
        "Outra",
        "Erro que não se enquadra adequadamente em nenhuma das demais categorias padrão.",
    ),
)
