# ADR-005 — Logging, correlação e health local da V0.1

- **Status:** Aceita
- **Data:** 2026-09-02
- **Escopo:** Etapa 5 da V0.1
- **Requisitos:** base técnica de `RF-067` e `RF-068`; `RN-001`; `RNF-018`,
  `RNF-022`, `RNF-032`, `RNF-068`–`RNF-070` e parcela local de `RNF-072`
- **Decisões controladas:** `ERR-V01-005`, `ERR-V01-007`
- **Testes:** `CT-099`, `CT-104`, `CT-131`, `CT-134`

## Decisão

`modules.operations` implementa a parcela operacional de `SDD-MOD-011` sem
persistência. Não existe `AuditEvent` na V0.1. Os logs são linhas JSON emitidas
pela biblioteca padrão do Python, com sanitização central no formatter. Não foi
adicionada dependência.

Todo evento contém `timestamp` UTC, `level`, `event_code`, `correlation_id`,
`operation`, `outcome` e `context`. O contexto admite apenas metadados técnicos
mínimos. Exceções são representadas por códigos e nomes de tipo; mensagens e
tracebacks não são incorporados aos eventos estruturados.

Chaves relacionadas a senha, segredo, token, autorização, cookie, sessão,
credencial, corpo, payload, conteúdo de estudo, resposta, caminho e conexão são
redigidas recursivamente. O valor efetivo de `SECRET_KEY` e credenciais embutidas
em texto também são removidos antes da serialização.

## Correlação

O identificador é um UUID transitório armazenado em `ContextVar`; não é entidade
de domínio. Um UUID válido recebido em `X-Correlation-ID` é propagado pela
requisição e devolvido no mesmo cabeçalho. Entrada ausente ou inválida gera novo
UUID. Bootstrap, seed e migração aceitam identificador opcional, criam um quando
necessário e preservam o contexto exterior em chamadas aninhadas.

## Catálogo técnico mínimo

- inicialização da aplicação;
- acesso HTTP local recusado;
- health concluído ou falhou;
- bootstrap iniciado, concluído ou falhou;
- seed iniciado, concluído ou falhou;
- migração iniciada, concluída ou falhou;
- `BACKUP_FAILED`, reservado para permitir o cenário de log de `CT-134` e a
  integração da etapa própria de backup, sem implementar backup nesta etapa.

Tentativas, ciclos, revisões, autorização remota, restauração, reconciliação e
auditoria funcional serão catalogados somente quando suas capacidades existirem.

## Contrato do diagnóstico local

O contrato mínimo escolhido para resolver a abertura permitida por
`ERR-V01-005` é `GET /health/`:

- `200`: `{"status":"healthy","checks":{"application":"ok","database":"ok"}}`;
- `503`: `{"status":"unhealthy","checks":{"application":"ok","database":"unavailable"}}`;
- `403`: `{"status":"forbidden"}` para endereço de cliente não loopback;
- a resposta inclui `X-Correlation-ID` e nunca inclui exceção, stack trace,
  caminho, configuração ou segredo.

A prontidão exige executar uma consulta mínima no banco. A fronteira HTTP inteira
permanece limitada a endereços loopback, além da allowlist de hosts já fixada no
ADR-002. Cabeçalhos de proxy não ampliam essa confiança local.

## Migração e inicialização

O comando `migrate` do Django é estendido apenas como adaptador operacional. Sua
semântica e opções originais são preservadas; o adaptador acrescenta
`--correlation-id` e eventos de início, sucesso e falha. A inicialização do app
emite versão e perfil, sem caminhos ou configuração sensível.

## Itens deliberadamente adiados

Logs remotos, métricas, alertas, telemetria externa, retenção/rotação operacional,
`AuditEvent`, auditoria funcional persistente, backup/restauração, interface,
questões, tentativas, ciclos, revisões e dashboard permanecem nas respectivas
etapas. `BACKUP_FAILED` no catálogo não implementa nem antecipa o mecanismo de
backup.
