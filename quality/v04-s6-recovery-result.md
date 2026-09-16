# V0.4-S6 — Evidência de recuperação e review A8

Data: 2026-09-16. Autoridade: contrato V0.4-S6; M/high. Baseline Architecture
v1.0 preservada. Auditoria inicial e decomposição em
`tasks/plans/v04-s6-backup-recovery.md`; operação em
`docs/V0.4_S6_Backup_e_Recuperacao.md`.

## Resultado técnico observado

- Testes focados/relacionados: **65 passed**, 21,37 s, exit 0:
  `python -m pytest tests/test_backup_restore.py tests/test_backup_recovery.py tests/test_integrity_checker.py tests/test_learning_foundation.py tests/test_stage5_promotion.py -q --tb=short`.
- **20 casos novos** em `tests/test_backup_recovery.py`: resíduo S1; hashes e
  repetição; checker apontando para restore tanto no negativo quanto no positivo
  com ativo divergente; exit 2/3 reais; cópia errada; corrupção com manifesto
  recalculado; permissão/espaço simulados; bloqueio real; overwrite; sidecars;
  paths; concorrência de publicação; arquivo/diretório ausente e WAL com
  sucesso/finding/cleanup. Mock de link cobre a guarda; não simula ataque de
  filesystem concorrente. Testes legados cobrem abertura em processo Django,
  migrations incompatíveis, perda do ativo, categorias, manifesto e logging.
- Ruff/formatação e mypy focados aprovados. Sem alteração em migrations/schema,
  catálogo S5, domínio S1-S4, Architecture, Skills ou gate.

## Ensaio operacional controlado

Comando executado com Python do venv:
`python scripts/verify_v04_recovery.py --output quality/v04-s6-recovery-drill.json`.
Exit **0**. Evidência estruturada no JSON; somente dados sintéticos em diretório
descartável, com origem explicitamente separada do banco real. Conduzido por
agente, sem alegação de sessão/aceite humano.

Ambiente observado: Windows, Python 3.13.15, SQLite 3.53.1, Django 5.2.17.
Backup: **655.360 bytes**. Estado conhecido: 2 questões ativas, 2 erros INITIAL,
1 classificação, 1 revisão de classificação, 2 ciclos, 2 revisões, 1 recibo,
24 migrations e 1 resíduo S1 sem classificação.

Os seis comandos reais terminaram em exit 0: checker na origem sintética,
backup, validação física, restore, checker sobre destino e abertura ORM em novo
processo. `integrity_check=ok`, zero FK findings e S5 saudável. Contagens
esperadas e SHA-256 do restore reconciliaram. Hashes do backup, manifesto e
principal sintético permaneceram inalterados.

Restore + checker externo + abertura/checagens: **2,691580 s** observados;
restore command: **1,024560 s**. Não inclui instalação, intervenção humana,
recuperação de dispositivo ou dados reais; esses tempos são `unknown`.
Não é SLA, BCR-1 ou piloto. RPO 24 h depende da frequência manual efetiva;
RTO objetivo 4 h; retenção mínima 7 diárias/4 semanais, sem automação nova.

## Review A8 profundo

Revisão pelo agente executor, baseada no diff real, contrato, callers,
testes positivos/negativos e ensaio. Não é aprovação humana independente.
Resultado: **APPROVED**, sem Blocker/Major aberto. Gate é controle separado.

Findings concretos tratados:

1. **Major — restore sem S5:** base fisicamente íntegra com data civil errada
   era publicável. Interface S5 integrada ao alias temporário; exit 2 impede
   publicação e exit 3 permanece distinto. Testes reais provam ambos.
2. **Major — resíduo S1 rejeitado:** consulta legada exigia classificação para
   todo erro VALID. Removida apenas essa exigência; S5/domínio preservados.
3. **Major — correspondência insuficiente:** contagens/estrutura não provavam
   cópia do arquivo esperado. Hash integral exige igualdade com manifesto;
   teste injeta outro banco SQLite válido e detecta divergência.
4. **Major — espera sem limite:** backup API podia repetir bloqueio sem fim.
   Callback com orçamento cooperativo e falha segura; bloqueio EXCLUSIVE real
   testado, sem publicar sucesso parcial.
5. **Major — temporários WAL:** teste reproduziu sidecars remanescentes após
   S5 read-only. Cleanup agora inclui apenas sidecars do temporário próprio,
   com conexão fechada, em sucesso/falha. Sidecars preexistentes no destino
   causam recusa e não são apagados.
6. **Correção de fixture:** teste legado de restore V0.3 gerava recibo com chave
   diferente da Attempt. Reproduzido finding `OPS-001` antes de corrigir a
   montagem; agora a origem é explicitamente verificada. Não houve relaxamento
   do checker nem alteração de produção fora de S6.
7. **Correção mínima de fixture S4:** o gate reproduziu seleção aleatória de
   `OTHER` por `.first()`, sem a descrição obrigatória. O teste agora seleciona
   `CONCEPTUAL` explicitamente; asserções e código S4 ficaram intactos. Reteste
   específico: 1 passed, 2,12 s, exit 0. Correção indispensável de montagem
   determinística, sem ampliar funcionalidades nem modificar o gate.

O primeiro gate parou em duas referências de patch de teste incompatíveis com
o mypy; alvos passaram a ser strings de import, mantendo a injeção de falha.
O segundo gate encontrou a fixture aleatória acima (321 passed, 1 failed;
88% de cobertura). Ambos terminaram com exit 1; não foram declarados GREEN.
O terceiro gate aprovou 322 testes (72,08 s; 88%), mas parou no detect-secrets
por falso positivo no SHA-256 sintético do relatório. O digest bruto de um
artefato descartável foi omitido do relatório; o executor continua exigindo
igualdade integral por hash antes/depois, e registra método/resultado. Nenhum
detector, allowlist, threshold ou gate foi alterado. O ensaio foi repetido com
exit 0 e os tempos finais acima.

Inspeções adicionais: proteção de origem/ativo, resolução de links/junctions,
publicação exclusiva inclusive colisão concorrente, falhas de permissão/espaço,
cleanup, manifesto/schema, read-only e ausência de repair, logging sem conteúdo,
correlação, mensagens recuperáveis, ausência de RPO/RTO inventado e de S7-S9.
Pré-backup automático não se aplica: não existe substituição do ativo. O guia
exige preservação do estado atual antes de futura adoção operacional.

Complexidade: cópia/hash sequenciais com memória limitada; reconciliação existente
e S5 em lote (18 consultas S5), sem novo N+1. Escala 10k/100k/100k não foi
medida nesta etapa; S8 mantém o hardening/BCR-1. Diretório local controlado pelo
operador é premissa; não se implementou sandbox contra troca maliciosa de
diretórios durante operações de filesystem.

## Gate e encerramento

`git diff --check`: aprovado, exit 0.

Gate autoritativo final:
`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.
Resultado **GREEN**, exit **0**, em **105,8 s**: 322 testes aprovados em
74,56 s, cobertura global 88%, perfis/checks, migrations (nenhuma nova), banco
vazio, formatação, Ruff, mypy, cobertura de domínio, detect-secrets e pip-audit
aprovados. Nenhuma vulnerabilidade conhecida foi encontrada.

O gate final foi a quarta execução: as três anteriores identificaram, em ordem,
dois alvos de patch incompatíveis com mypy, uma fixture S4 não determinística e
o digest sintético sinalizado como alta entropia. Todos foram corrigidos sem
alterar controles. A conclusão registra somente o gate final GREEN.

S6 concluída e elegível para arquivamento. Sem P0/P1 aplicável aberto; nenhuma
migration/schema change, restore destrutivo, dado pessoal real, S7, S8 ou S9.
