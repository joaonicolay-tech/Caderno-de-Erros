# ADR-002 — Perfis Django e isolamento de testes da V0.1

- **Status:** Aceita
- **Data:** 2026-09-01
- **Escopo:** Etapa 2 da V0.1
- **Requisitos:** base técnica de `RF-067`; `RNF-012`, `RNF-018`, `RNF-033`,
  `RNF-051`–`RNF-054`, `RNF-056`, `RNF-079`, `RNF-080`
- **Testes:** `CT-081`, `CT-099`, `CT-104`, `CT-123`, `CT-127`, `CT-130`

## Decisão

O projeto Django reside em `src/config`, com `manage.py` na raiz e três módulos
de settings explícitos:

- `config.settings.development`;
- `config.settings.test`;
- `config.settings.production_local`.

`manage.py` usa desenvolvimento apenas como padrão de trabalho local. WSGI e
ASGI usam produção local por padrão, que exige `CEI_SECRET_KEY`, mantém
`DEBUG=False` e recusa hosts diferentes de `127.0.0.1`, `localhost` e `[::1]`.

O perfil de teste não lê caminhos de banco ou segredo dos outros perfis. Cada
processo cria um diretório temporário exclusivo e configura SQLite em arquivo,
preservando a semântica principal do MVP sem apontar para banco de uso real.
pytest-django e o plugin mypy/django-stubs carregam exclusivamente esse perfil.
Os artefatos temporários do pytest ficam em `.pytest-tmp/`, diretório ignorado
e descartável dentro do workspace, evitando dependência das permissões do diretório
temporário global do Windows.

## Ausência deliberada de aplicações e models

`INSTALLED_APPS` permanece vazio nesta etapa. Em particular,
`django.contrib.auth` não é habilitado: criar suas migrações introduziria o User
padrão antes do User customizado exigido pela próxima etapa. Também não são
criados pacotes vazios para os módulos futuros do SDD.

Portanto, `migrate` e `makemigrations --check` validam corretamente uma fundação
sem migrações próprias. A primeira alteração de esquema será feita junto das
entidades formalmente autorizadas.

## Configuração externa e fronteira local

| Variável | Perfil | Comportamento |
|---|---|---|
| `CEI_SECRET_KEY` | produção local | obrigatória, sem default e com mínimo de 50 caracteres |
| `CEI_DEVELOPMENT_DB` | desenvolvimento | caminho SQLite; default `var/development.sqlite3` |
| `CEI_PRODUCTION_LOCAL_DB` | produção local | caminho SQLite; default `var/production_local.sqlite3` |
| `CEI_ALLOWED_HOSTS` | desenvolvimento/produção local | aceita somente hosts locais aprovados |

O perfil de teste ignora intencionalmente todas essas variáveis. Alterar o
endereço do servidor para uma interface não local não pertence a esta arquitetura
e aciona os requisitos de implantação remota de `RNF-012`.

## Evidência exigida

- os três perfis passam por `django.setup()`, conexão SQLite e system checks;
- banco sentinela indicado nas variáveis reais permanece byte a byte inalterado;
- produção local falha sem chave externa e rejeita `0.0.0.0`;
- pytest cria banco SQLite descartável no diretório temporário do sistema e mantém
  seus demais artefatos temporários em `.pytest-tmp/`;
- `mypy_django_plugin.main` usa `config.settings.test`;
- o gate único executa checks, migração vazia, lint, mypy, testes, segredos e
  vulnerabilidades.

## Itens adiados

User customizado, Workspace, primeiro acesso, Clock/Calendar, categorias, seed,
logging definitivo, health, layout, backup e todas as capacidades posteriores
continuam fora desta etapa.
