# ADR-007 — Backup e restauração mínima SQLite da V0.1

- **Status:** Aceita
- **Data:** 2026-09-03
- **Escopo:** Etapa 7 da V0.1
- **Decisão controlada:** aplicação de `ERR-V01-006`
- **Requisitos:** base técnica de `RF-067`; `RF-068`; `RN-001`; `RNF-033`–`RNF-038`,
  `RNF-070`
- **Arquitetura/fluxo:** `SDD-MOD-010`, `SDD-ADR-006`, seção 21.1 do SDD e parcela
  técnica de `FL-022`
- **Testes:** `CT-081`, `CT-132`, `CT-133`, parcela de corrupção aplicável de
  `CT-114`, além da regressão de `CT-134`

## Contexto e limite da decisão

A fundação precisa provar recuperação antes de receber dados valiosos, mas a V0.1
ainda contém somente `User`, `Workspace`, preferências de locale/fuso, migrações e
as dez categorias padrão. Portanto, esta decisão implementa um procedimento técnico
para o arquivo SQLite completo. Ela não define `CEI-EXPORT-1.0`, importação lógica,
mesclagem, troca do banco ativo nem interface de restauração.

## Decisão

`modules.data_management` implementa três operações explícitas:

1. `backup_sqlite` cria e valida um snapshot;
2. `validate_backup` confere o artefato sem modificar banco algum;
3. `restore_backup` materializa e reconcilia o snapshot em um novo destino isolado.

O snapshot usa `sqlite3.Connection.backup()`, com origem aberta em modo somente
leitura. Essa API do próprio SQLite copia um ponto consistente dos dados confirmados
e evita a cópia arbitrária do arquivo enquanto ele pode estar em uso. As conexões
são fechadas explicitamente, inclusive no Windows, antes da sincronização e da
publicação dos arquivos.

O chamador escolhe destinos explícitos. Diretórios precisam existir e nenhum comando
sobrescreve arquivo existente. Artefatos são preparados com nomes temporários no
mesmo diretório, sincronizados e publicados apenas depois das verificações. A
publicação usa uma primitiva que falha se o nome final já existir (`rename` no
Windows; hard link no fallback compatível), sem a semântica de sobrescrita de
`replace`. Em falha, arquivos criados pela operação são removidos; o resultado do
cleanup integra somente o contexto técnico sanitizado do evento.

## Formato do manifesto

Cada arquivo `nome.sqlite3` recebe o sidecar `nome.sqlite3.manifest.json`, em UTF-8,
com exatamente:

```json
{
  "format": "CEI-SQLITE-BACKUP",
  "format_version": "1.0",
  "created_at": "2026-09-03T12:00:00.000+00:00",
  "size_bytes": 123456,
  "sha256": "64 caracteres hexadecimais minúsculos"
}
```

O manifesto não contém caminho, segredo, credencial, conteúdo de estudo, nome do
Workspace nem dado pessoal. `created_at` é um instante ISO 8601 em UTC. O formato é
próprio do backup físico técnico e não é o formato de exportação V1.

## Validação e ordem de confiança

A validação rejeita, nesta ordem, ausência/estrutura inválida do manifesto, formato
ou versão desconhecida, tamanho divergente, SHA-256 divergente e falha de
`PRAGMA integrity_check`/`PRAGMA foreign_key_check`. Nenhuma confirmação positiva é
emitida antes do fim dessa sequência.

A restauração repete essa validação **antes** de criar o banco de destino. Depois,
copia para um arquivo temporário e exige:

- conjunto de migrações aplicadas exatamente igual às migrações da versão corrente;
- exatamente um `User` local ativo com o UUID canônico;
- exatamente um `Workspace` local com UUID/proprietário canônicos;
- locale `pt-BR` e identificador de fuso IANA válido;
- exatamente as dez categorias padrão vinculadas ao Workspace, com códigos e textos
  canônicos correntes;
- integridade SQLite e ausência de violações de chave estrangeira.

Essa reconciliação é somente leitura. O bootstrap não é chamado e nenhum registro é
recriado para mascarar ausência ou corrupção. O arquivo restaurado só recebe o nome
final no destino isolado depois de todas as verificações.

## Logging e correlação

Foram ativados os eventos operacionais mínimos `BACKUP_STARTED`,
`BACKUP_SUCCEEDED`, `BACKUP_FAILED`, `BACKUP_VALIDATION_STARTED`,
`BACKUP_VALIDATION_SUCCEEDED`, `BACKUP_VALIDATION_FAILED`, `RESTORE_STARTED`,
`RESTORE_VALIDATED` e `RESTORE_FAILED`. Uma operação compartilha o UUID de correlação
fornecido ou gerado. Contextos registram apenas resultado, contagens, tamanho, tipo
técnico do erro e situação do cleanup; caminhos e mensagens de exceção não são
registrados.

## Segurança operacional

O backup contém os mesmos dados privados do banco e herda a proteção da conta e do
sistema de arquivos local. Se for levado para fora do dispositivo protegido, deve
receber proteção adequada antes do transporte. O mecanismo não substitui o banco
ativo e não oferece opção de sobrescrita. A adoção de um arquivo restaurado continua
uma decisão operacional posterior à validação e fora do comando da V0.1.

## Evidências da Etapa 7

- backup e manifesto são criados em diretório descartável;
- o SHA-256 é recalculado por validação independente;
- uma escrita não confirmada em banco WAL não aparece no snapshot;
- alteração de byte e checksum divergente bloqueiam antes do destino;
- restauração abre em novo processo Django e preserva identidade, Workspace, locale,
  fuso, migrações e dez categorias;
- restauração isolada permanece disponível quando o arquivo ativo foi perdido;
- categoria ou migração ausente é rejeitada sem bootstrap corretivo;
- destino preexistente permanece byte a byte inalterado;
- sucesso e falha possuem logs correlacionados e sem sentinelas privadas.

## Itens deliberadamente posteriores

- A política operacional de RPO de 24 horas, RTO de 4 horas, sete versões diárias e
  quatro semanais (`RNF-035`, `RNF-037`) deve estar implantada e exercitada antes do
  piloto contínuo com dados reais; a V0.1 não possui scheduler, rotação nem serviço
  residente.
- A restauração de base representativa de versões anteriores e falha de migração
  (`CT-082`, `CT-083`) começa nas fases indicadas pelo Plano de Testes.
- Backup de conteúdo representativo, questões, tentativas, ciclos e revisões só pode
  ser testado quando essas entidades existirem.
- Criptografia fora do dispositivo, nuvem e backup centralizado dependem da forma de
  implantação e não são funcionalidades da V0.1.
- Exportação `CEI-EXPORT-1.0`, restauração pela interface, confirmação de impacto,
  pré-backup do banco ativo, importação lógica e relatórios funcionais pertencem à
  V0.5-C/V1.

Assim, `CT-132` e `CT-133` são atendidos para a fundação V0.1 sem transformar a
prova mínima em funcionalidade futura de produto.
