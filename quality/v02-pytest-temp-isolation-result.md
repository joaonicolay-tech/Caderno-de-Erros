# V0.2 — Correção operacional do isolamento temporário do pytest

- Data: 2026-09-06.
- Escopo: correção pré-Etapa 7; nenhuma funcionalidade de produto foi alterada.
- Causa: `--basetemp=.tools/pytest-tmp` reutilizava uma pasta estática entre
  execuções. No Windows, resíduos dessa pasta podem manter ACL incompatível ou
  bloqueio de processo e provocar `PermissionError` antes de os testes rodarem.
- Solução: a configuração compartilhada deixou de fixar `basetemp`; o gate cria
  um caminho único com GUID no temporário do sistema e o passa ao pytest a cada
  execução. Uma falha ou ACL residual de execução anterior, portanto, não é
  reutilizada.
- Auditoria: `pip-audit --local --strict` permanece obrigatória. Se não produzir
  relatório de vulnerabilidades válido, o gate falha explicitamente como erro
  operacional (por exemplo, rede ou ferramenta), sem resultar em PASS artificial.
- Suíte: 183 aprovados.
- Gate autoritativo: GREEN, exit code 0; `pip-audit` informou nenhuma
  vulnerabilidade conhecida.
- Migrations: `makemigrations --check --dry-run` sem alterações; migrations
  protegidas validadas pelo gate.
- Etapa 7: continua formalmente liberada e não iniciada.
