# ADR-003 — Identidade, Workspace e tempo da V0.1

- **Status:** Aceita
- **Data:** 2026-09-02
- **Escopo:** Etapa 3 da V0.1
- **Requisitos:** `RF-001`–`RF-003`, base de `RF-067`; `RN-001`–`RN-005`;
  `RNF-012`, `RNF-013`, `RNF-027`, `RNF-030`, `RNF-031`, `RNF-066`,
  `RNF-067`, `RNF-074`, `RNF-075`
- **Testes:** `CT-001`, `CT-002`, `CT-073`, `CT-074`, `CT-081`, parte
  aplicável de `CT-129` e `CT-135`

## Decisão

O módulo implementado nesta etapa é `modules.accounts`, correspondente a
`SDD-MOD-001`. Ele contém o `User` customizado e `Workspace`; nenhum outro módulo
do catálogo do SDD é criado antecipadamente.

O `User` herda o mecanismo de credenciais seguro de `AbstractBaseUser`, usa UUID
como chave primária e possui exatamente os dados funcionais definidos no Modelo de
Dados: nome de exibição opcional, e-mail opcional e único quando informado, estado
e datas de controle. A autenticação remota, permissões administrativas e interface
de login continuam fora da V0.1 local.

`AUTH_USER_MODEL` aponta para `accounts.User` antes da ativação de
`django.contrib.auth`. A migração `accounts.0001_initial` é a raiz do módulo e
cria o User customizado e o Workspace; nenhuma tabela `auth_user` existe.

O `Workspace` usa UUID, FK `PROTECT` para o proprietário, locale inicial `pt-BR`,
fuso IANA obrigatório, datas de controle e `lock_version` positivo. Consultas e
alterações recebem simultaneamente o identificador do espaço e o do proprietário,
sem confiar apenas no identificador fornecido pelo cliente.

## Bootstrap local

O bootstrap usa UUIDs técnicos estáveis para a identidade e o espaço locais. Essa
escolha torna a operação naturalmente idempotente e faz a restrição de chave
primária impedir duplicação mesmo sob repetição. User e Workspace são criados em
uma única transação; falha no segundo reverte o primeiro. Uma execução posterior
recupera o mesmo espaço e não altera silenciosamente o fuso já escolhido.

O fuso é argumento obrigatório e validado antes da transação; não existe default
derivado do servidor ou navegador. O nome técnico inicial do espaço é `Meu espaço`
e pode ser informado explicitamente pelo chamador. A identidade local recebe senha
inutilizável, pois o perfil estritamente local dispensa login conforme `RNF-012`.

`FL-023` e `CT-129` completos também incluem as dez categorias padrão. A
solicitação da Etapa 3 proíbe antecipar `ErrorCategory`; por isso, nesta etapa a
atomicidade e a idempotência cobrem somente User/Workspace. A Etapa 4 deverá
estender o mesmo caso de uso para incluir o seed antes da liberação da V0.1.

## Primeiro acesso e mudança de fuso

A fundação expõe um serviço e o comando `bootstrap_local`, mas não antecipa layout,
formulário ou rota. A mudança posterior:

- valida novamente o identificador IANA;
- exige confirmação explícita;
- mantém o valor anterior quando cancelada ou inválida;
- autoriza por proprietário e Workspace;
- usa atualização condicional por `lock_version`, recusando sobrescrita perdida;
- informa que “hoje” e cálculos futuros mudam, sem reescrever história.

Como não há `Review` nesta etapa, não existe recálculo de fila, reagendamento,
ciclo ou evento funcional persistente. Esses comportamentos permanecem na V0.3.

## Semântica temporal

`shared.domain.time` implementa os objetos `Instant`, `LocalDate` e `TimeZoneId`,
o contrato `Clock` e os adaptadores `SystemClock`/`FixedClock`. `Calendar` deriva
“hoje” de um Clock e de um TimeZoneId explícitos e soma dias sobre LocalDate.

`Instant` exige datetime consciente de fuso e normaliza para UTC. `TimeZoneId`
usa `zoneinfo.ZoneInfo`, preservando as regras históricas IANA disponíveis no
runtime fixado. Nenhum cálculo de data civil do domínio consulta diretamente o
relógio global.

## Evidência exigida

- migrações aplicam desde banco vazio e criam `accounts_user`, nunca `auth_user`;
- UUID, FK, `PROTECT`, status e `lock_version` constam do schema inicial;
- bootstrap repetido mantém exatamente um User e um Workspace;
- falha controlada do Workspace reverte a criação do User;
- fuso inválido não persiste estado parcial;
- cancelamento, confirmação, persistência e conflito de versão são testados;
- acesso cruzado entre dois proprietários é recusado;
- um instante fixo produz datas distintas em São Paulo e Tóquio;
- o gate único continua validando migrações, tipos, testes, segredos e dependências.

## Itens adiados

`ErrorCategory` e seed, apresentação do primeiro acesso, autenticação remota,
logging estruturado definitivo, health, backup/restauração e todos os módulos de
conteúdo, tentativa, revisão e dashboard permanecem fora desta etapa.
