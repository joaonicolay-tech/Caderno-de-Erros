# A8 — Política formal de code review

Status final: concluída e arquivada em 12 de setembro de 2026.

## Contrato executado

- Task ID: A8
- Product version: V0.3 operational architecture
- Stage: A8 — Formal Code Review Policy
- Task type: operational architecture / code review policy
- Size: M
- Risk: low

### Goal

Formalizar uma política concisa e reutilizável de code review integrada à arquitetura operacional, elevando a qualidade da revisão sem duplicar o gate nem criar sobrecarga desproporcional.

### Escopo, proteção e critérios

O escopo autorizado cobriu a auditoria da prática atual, uma fonte principal de política, integração documental mínima e o registro do encerramento. Permaneceram protegidos Django, regras de negócio, migrations, schema, baseline V0.3, A7 salvo referência mínima, Skills salvo integração comprovadamente necessária, gate, configuração pessoal, A9 e V0.4.

A política deveria definir prioridades, severidade, aprovação/bloqueio e profundidades proporcionais; usar Expected Scope e Protected Scope como entradas; cobrir regressões, segurança, integridade, migrations, testes, documentação e efeitos colaterais; manter baixa duplicação; validar cenários conceituais; passar diff check e gate; arquivar A8 e deixar current sem autorização.

## Resultado e auditoria

A prática anterior já distribuía controles úteis: tasks/current.md define autorização e escopo; A2/A3/A4 definem contrato, consulta proporcional e planos; as quatro Skills separam início, implementação, gate e encerramento; A7 calibra risco e métricas; e o gate reúne verificações técnicas. A lacuna era uma fonte principal que ordenasse a revisão e definisse profundidade, findings e decisão.

docs/review/code-review.md preenche essa lacuna sem replicar autoridades. Ela prioriza critérios, regressões e escopo antes de segurança, integridade, migrations, comportamento, testes e documentação; define revisões leve, padrão e profunda; severidades Blocker/Major/Minor; APPROVED, APPROVED WITH NOTES, CHANGES REQUIRED e INCONCLUSIVE; e formato curto de finding. Expected Scope e Protected Scope são entradas explícitas e finding fora da tarefa é registrado, não corrigido silenciosamente.

Os casos conceituais A–H foram validados na política: documentação XS/low, feature Django M/medium, bugfix de segurança pequeno, migration L/high, refactor, gate verde sem teste essencial, mudança correta fora do escopo e finding independente. A integração necessária foi somente o índice em docs/README.md. As Skills já referenciam as fontes de verdade; não foram alteradas e nenhuma nova Skill foi criada. A duplicação observada é baixa.

## Verificação e encerramento

- git diff --check: aprovado antes do gate.
- Gate autoritativo: GREEN na primeira tentativa, exit code 0, em 88,9 s.
- Testes: 280 aprovados; cobertura global 87%.
- Migrations, Ruff, mypy, detect-secrets, cobertura de domínio e auditoria de vulnerabilidades: aprovados.
- Métrica A8 registrada com fatos disponíveis; reasoning, duração e quotas indisponíveis permanecem unknown.

Não houve alteração de funcionalidade Django, regras de negócio, migrations, schema, gate, configuração pessoal ou Skills. A9 e V0.4 não foram iniciadas. Não houve commit, push, tag ou release.

## Próximo estado

tasks/current.md retorna a Status: NO_TASK_AUTHORIZED. Qualquer trabalho posterior, inclusive A9 ou V0.4, exige nova autorização formal.
