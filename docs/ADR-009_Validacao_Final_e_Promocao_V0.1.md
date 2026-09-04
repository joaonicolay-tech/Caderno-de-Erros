# ADR-009 — Validação final e promoção da V0.1

- **Status:** Aceita — promoção concluída
- **Data:** 2026-09-03
- **Escopo:** Etapa 9 da V0.1
- **Requisitos:** `RNF-053`, `RNF-056`, `RNF-063`, `RNF-080`
- **Testes:** `CT-123`, `CT-127`, `CT-128`, `CT-136`
- **Decisões relacionadas:** `ADR-001`, `ADR-006`, `ADR-007`, `ADR-008`,
  `RD-DEC-002`, `RD-DEC-011`
- **Decisão final:** **PROMOVIDA**

## Decisão

A fundação está tecnicamente executável, a instalação limpa `CT-127` foi aprovada e a
checklist integral de `CT-136` foi executada manualmente com sucesso em Chrome e Edge.
Depois da incorporação dessa evidência, o gate autoritativo foi executado novamente
com exit code 0. Não resta P0/P1 aplicável nem defeito S1/S2 conhecido; todos os
critérios obrigatórios da matriz estão em PASS. A V0.1 é, portanto, **PROMOVIDA**.

Esta decisão não publica release externa nem autoriza `push`. A situação da tag local
é registrada separadamente após a verificação do estado Git.

## Instalação Windows limpa — CT-127

O exercício ocorreu em uma cópia descartável sob
`%TEMP%\cei-v01-stage9-<identificador>`, criada apenas com os arquivos do projeto.
Antes do início foram confirmadas as ausências de `.venv`, `.tools`, `.pytest-tmp`,
`.env`, `var`, `backups` e `recovery`. Nenhum banco ou cache do workspace original foi
copiado.

Pré-requisitos preexistentes: Windows 11 x64, PowerShell e Git. `uv` não estava no
`PATH`. O instalador oficial fixado no README obteve `uv 0.12.7` para um diretório
interno à cópia. Cache e instalação de Python também apontaram para diretórios novos
dessa cópia.

| Passo | Evidência | Resultado |
|---|---|---|
| Instalar `uv` | download oficial da versão `0.12.7` | PASS |
| Sincronizar | `uv sync --locked`, sem cache prévio | PASS |
| Runtime | Python `3.13.15`, Django `5.2.17`, SQLite `3.53.1` | PASS |
| Migrar do zero | 16 migrações aplicadas em SQLite novo | PASS |
| Bootstrap duas vezes | primeira criou; segunda retornou `created_count=0` | PASS |
| Reconciliar fundação | 1 User, 1 Workspace, `pt-BR`, `America/Sao_Paulo`, 10 categorias | PASS |
| Iniciar aplicação | servidor restrito a `127.0.0.1` | PASS |
| Health | HTTP 200, `healthy`, aplicação e banco `ok` | PASS |
| Backup | snapshot consistente de 110592 bytes e manifesto | PASS |
| Validar backup | formato 1.0, tamanho e checksum aceitos | PASS |
| Restaurar | novo destino isolado, 16 migrações reconciliadas | PASS |
| Iniciar restaurado | check e health HTTP 200 sobre a cópia restaurada | PASS |
| Gate limpo | 91 testes; segurança aprovada; exit code 0; 43,9 s | PASS |

O exercício encontrou e corrigiu no README um nome de atributo incorreto no comando
de conferência (`timezone` para `timezone_name`). O primeiro gate na cópia também
registrou a proteção Git `dubious ownership`, causada por a cópia ser criada pelo
sandbox e validada pelo usuário Windows. A repetição usou `safe.directory` somente no
ambiente do processo e para aquele caminho descartável; nenhuma configuração global
ou regra do gate foi alterada.

A evidência é uma instalação nova no mesmo Windows físico, não uma segunda máquina ou
VM. Ainda assim, não reutiliza ambiente virtual, runtime Python, cache, banco,
configuração privada ou artefato gerado da instalação original e satisfaz a definição
aplicável de `CT-127`.

## Browser, acessibilidade e CT-136

Chrome `152.0.7977.65` e Edge `152.0.4191.53`, as versões registradas no `ADR-001`,
foram validados manualmente. Em ambos, a checklist integral foi concluída sem falha:
primeiro acesso, escolha explícita de `America/Sao_Paulo`, português/Unicode, tela
inicial, ausência de links futuros, teclado, ordem e visibilidade de foco, skip link,
labels, erros e feedback não dependente apenas de cor, cancelamento, confirmação,
persistência, zoom de 200%, viewport aproximado de 360 px, desktop, responsividade e
ausência de rolagem horizontal indevida.

Portanto:

- Chrome `152.0.7977.65`: **PASS**;
- Edge `152.0.4191.53`: **PASS**;
- `CT-136`: **PASS integral**;
- parcela estrutural V0.1 relacionada a `CT-128`: **PASS** pelos testes automatizados
  de HTML semântico, contraste, foco e CSS responsivo;
- `CT-128` completo: **N/A nesta versão**, pois seu gate autoritativo permanece em
  V0.4/V1 conforme o Plano de Testes.

### Checklist manual executada

A lista abaixo foi executada separadamente no Chrome e no Edge, com resultado PASS em
todos os itens:

1. Com banco novo, abrir `/` e confirmar redirecionamento para `/primeiro-acesso/`.
2. Usar somente `Tab`, `Shift+Tab`, setas, espaço e `Enter`; confirmar que o skip link
   é o primeiro foco útil, a ordem é lógica e todo foco é visível.
3. Confirmar `lang="pt-BR"`, títulos, labels persistentes e ajuda associada ao seletor.
4. Enviar sem fuso; confirmar foco no primeiro erro, `aria-invalid`, mensagem associada
   e distinção por texto/borda, sem depender exclusivamente de cor.
5. Selecionar `America/Sao_Paulo`, concluir e confirmar feedback textual e Unicode.
6. Na tela inicial, confirmar 1 Workspace, fuso efetivo e ausência de links para
   questões, tentativas, revisões, dashboard, busca ou outras funções futuras.
7. Abrir Configurações, escolher outro fuso e cancelar; confirmar valor original.
8. Repetir e confirmar; recarregar e confirmar persistência do novo fuso.
9. Se houver duas sessões/abas controladas, submeter `lock_version` obsoleto e confirmar
   conflito textual, estado atual preservado e exigência de nova confirmação.
10. Em 360 px e depois em desktop comum, percorrer todas as telas sem perda de ação,
    conteúdo truncado ou rolagem horizontal inadequada.
11. Repetir com zoom de 200% e em largura ampla até 1920 px.
12. Confirmar que sucesso, cancelamento, erro e conflito continuam compreensíveis sem cor.

Nenhuma falha foi identificada. A evidência manual complementa, sem substituir, os
testes estruturais automatizados já incorporados ao gate.

## Matriz objetiva de conclusão da V0.1

| Critério | Estado | Evidência |
|---|---|---|
| Iniciar seguindo somente o README | PASS | instalação descartável e correção validada |
| Migrações aplicam do zero | PASS | banco novo e `CT-081` |
| Suíte isolada não toca dados reais | PASS | 91 testes e `CT-130` |
| Workspace, locale e fuso persistem | PASS | reconciliação e `CT-002`/`CT-129` |
| Clock/Calendar reproduzíveis | PASS | `CT-135` |
| Dez categorias sem duplicação | PASS | dois bootstraps e `CT-129` |
| Falha obrigatória bloqueia gate | PASS | `ADR-008` e testes negativos |
| Sem segredo/conteúdo privado em logs | PASS | `CT-099`/`CT-134` |
| Backup/restauração mínima | PASS | smoke limpo e `CT-132`/`CT-133` |
| Smoke das capacidades V0.1 | PASS | `CT-123` |
| Instalação Windows limpa | PASS | `CT-127` |
| Browser/acessibilidade base | PASS | `CT-136` manual em Chrome e Edge |
| Parcela estrutural V0.1 de responsividade | PASS | testes de interface; `CT-128` completo é futuro |
| Gate autoritativo final | PASS | exit code 0; 91 testes; reexecutado após `CT-136` |
| P0 aplicável aberto | PASS | nenhum identificado |
| P1 aplicável aberto | PASS | nenhum identificado |
| Defeito S1/S2 aberto | PASS | nenhum identificado |
| Migrações históricas preservadas | PASS | hashes e ausência de migração pendente |
| Funcionalidade V0.2+ não antecipada | PASS | inspeção de módulos, rotas e navegação |
| Workflow específico de CI | N/A nesta versão | `RNF-080` aceita comando único; decisão do `ADR-008` |
| Migração de versão anterior | N/A nesta versão | V0.1 não possui release anterior suportada |

## Pendências e promoção

As correções `COR-P1-003`–`COR-P1-006` e o restante futuro de `COR-P1-001` continuam
nos marcos definidos pelo Gate documental e não bloqueiam a V0.1. Questões,
tentativas, revisões, dashboard, busca, categorias pessoais, autenticação remota, API,
notificações, PWA e capacidades de V0.2+ não foram antecipadas.

Não permanece P0 ou P1 aplicável à conclusão da V0.1, nem defeito S1/S2 conhecido.
Todos os critérios obrigatórios estão em PASS e a versão está formalmente promovida.
As pendências listadas acima pertencem a versões posteriores e não alteram essa
decisão. A criação de tag local depende de o commit correspondente conter toda esta
evidência; nenhum `push` ou release externo integra esta decisão.
