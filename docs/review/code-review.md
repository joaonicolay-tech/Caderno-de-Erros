# Política de code review

## Finalidade

Code review procura defeitos, riscos, regressões e violações de contrato — não
preferências pessoais de estilo. Um finding precisa apontar impacto concreto;
preferências estéticas podem ser anotadas como sugestão, nunca apresentadas como
impedimento de conclusão.

Esta política serve a revisão humana, por agente ou assistida. Ela complementa,
não substitui, `AGENTS.md`, o contrato em `tasks/current.md`, A2, A3, A4, A7,
testes e `scripts/quality.ps1`.

## Começo e prioridade

Comece pelo diff real e por `tasks/current.md`. Confirme primeiro que a mudança
resolve o **Goal**, atende aos critérios de aceite e `Done When`, pertence ao
**Expected Scope**, preserva o **Protected Scope** e respeita as **Constraints**.
Uma mudança tecnicamente boa, mas fora do escopo, é um finding.

Inspecione nesta ordem, aprofundando somente o que for aplicável:

1. critérios de aceite, regressões e escopo;
2. segurança, integridade de dados e migrations;
3. regras de negócio, erros e efeitos colaterais;
4. testes — sua pertinência e força, não só sua execução;
5. documentação necessária e clareza/manutenibilidade com impacto concreto.

O diff é o ponto de partida, não uma fronteira cega. Abra chamadas, contratos,
testes, modelos ou migrations relacionados somente quando necessário, conforme
A3. Se o contrato for internamente incoerente — por exemplo, `Done When` não
concluir o Goal ou persistir instrução transitória — o resultado é inconclusivo
até haver esclarecimento ou correção autorizada.

## Profundidade proporcional

| Profundidade | Quando usar | Foco mínimo |
| --- | --- | --- |
| Leve | XS/S, baixo risco, documentação ou mudança mecânica sem comportamento relevante | Contrato, diff, regressão óbvia e verificação prevista. |
| Padrão | Maioria das tarefas S/M | Contrato, comportamento, escopo, regressões, testes, integridade e documentação aplicáveis. |
| Profunda | Risco high/critical, migration, segurança, integridade, múltiplos módulos, arquitetura, dados persistentes críticos ou refactor amplo | Invariantes, failure modes, rollback, segurança, cobertura real e impacto sistêmico. |

Tamanho não reduz risco: uma correção pequena de segurança pode exigir revisão
profunda. A7 orienta a calibração operacional de risco, modelo e reasoning;
não altera a autorização funcional.

## Pontos de atenção orientados a risco

- **Regressões:** procure comportamento quebrado ou desaparecido, contratos
  silenciosamente alterados, fluxos existentes, estados e dados antigos, e
  efeitos colaterais não planejados. Não presuma que a suíte atual os cobre.
- **Segurança:** quando pertinente, examine autenticação/autorização, exposição
  e logs de dados, validação, CSRF, escaping, secrets, permissões, arquivos,
  execução de comandos, dependências e configuração. Não invente ameaças sem
  relação com a mudança.
- **Integridade:** quando pertinente, examine invariantes, atomicidade,
  transações, consistência entre entidades, estados impossíveis, duplicação,
  relacionamentos, deleção/arquivamento, timestamps, histórico e idempotência.
- **Migrations:** elevam a revisão para profunda. Verifique dados existentes,
  default e nullability, constraints/unicidade, ordem e dependências,
  reversibilidade/rollback quando aplicável, custo, perda de dados e
  compatibilidade entre schema e código. Não reescreva migrations históricas.
- **Testes:** verifique cobertura do novo comportamento, regressões, negativos
  e bordas relevantes; prefira testes que falhariam para uma implementação
  errada. Aponte mocks excessivos, asserts fracos e acoplamento indevido quando
  produzirem lacuna concreta. Gate verde não prova suficiência.
- **Documentação:** atualize ou peça atualização somente se requisito,
  comportamento observável, decisão, fluxo, guia ou estado passou a divergir.

`quality.ps1` GREEN não aprova automaticamente uma revisão; revisão aprovada
não dispensa o gate. São controles complementares e o reviewer não modifica o
gate para acomodar uma alteração.

## Findings e decisão

Registre findings de forma curta: `[Severidade] arquivo:linha — problema;
impacto; evidência; direção segura para correção.` Não escreva ensaios quando
poucas linhas bastam.

| Severidade | Significado |
| --- | --- |
| Blocker | Não aprovar: perda/corrupção de dados, vulnerabilidade relevante, violação clara de Protected Scope, requisito essencial ausente, regressão crítica ou migration perigosa. |
| Major | Problema real a corrigir normalmente antes da conclusão: comportamento incorreto, teste relevante ausente, borda importante, integridade ou erro inadequado. |
| Minor | Impacto limitado, porém concreto: manutenção prejudicada, documentação necessária ausente ou simplificação relevante. |

Nits e sugestões não são findings formais. O resultado é **APPROVED** sem
Blocker/Major aberto e com critérios essenciais comprovados; **APPROVED WITH
NOTES** com observações não bloqueadoras; **CHANGES REQUIRED** com finding a
resolver; ou **INCONCLUSIVE** quando falta evidência confiável — inclusive por
infraestrutura, sandbox, ACL, rede ou auditoria indisponível. Inconclusivo não
é aprovação e incidente de infraestrutura não é defeito da implementação sem
evidência.

Um problema real fora da tarefa deve ser registrado, não corrigido
silenciosamente nem usado para expandir o contrato. Ele bloqueia se torna a
alteração atual insegura; caso independente, vira insumo de tarefa futura.

## Calibração conceitual

| Caso | Profundidade e resultado esperado |
| --- | --- |
| A — documentação XS/low | Leve: contrato, diff, regressão documental e verificação prevista. |
| B — feature Django M/medium | Padrão: comportamento, regressões, testes, escopo, integridade e documentação aplicáveis. |
| C — bugfix pequeno de segurança | Profunda: ameaça concreta, controles, negativos e regressão; tamanho não reduz a análise. |
| D — migration L/high | Profunda: dados existentes, schema/código, integridade, rollback, custo e testes. |
| E — refactor sem mudança funcional | Padrão ou profunda conforme alcance: equivalência comportamental e regressões, não só compilação. |
| F — gate GREEN, teste essencial ausente | CHANGES REQUIRED: gate não substitui teste pertinente. |
| G — mudança correta fora de Expected Scope | Finding de escopo; não aprovar nem incorporar silenciosamente. |
| H — finding real fora da tarefa | Registrar; bloquear só se deixar a mudança insegura, senão encaminhar para tarefa futura. |

## Relação com o fluxo

`start-task`, `implement-current-task`, `run-quality-gate` e `finish-task`
continuam fontes concisas e independentes do fluxo. A evidência de revisão é
considerada no encerramento quando aplicável, sem criar Skill, checklist
universal ou pipeline automático. A7 orienta a proporcionalidade operacional e
o seu JSONL recebe somente fatos disponíveis ao encerrar a tarefa.

