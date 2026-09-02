# Caderno de Erros

Sistema para registro, classificação e revisão de erros de estudo.

A documentação oficial do projeto está localizada em `/docs`.

## Estado atual

A Etapa 1 da V0.1 fixa apenas a toolchain. O projeto Django ainda não foi criado.

Pré-requisitos do ambiente validado:

- Windows 11 x64;
- PowerShell 5.1 ou posterior;
- Git;
- `uv 0.12.7`.

Instalação exata do `uv` no Windows:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/0.12.7/install.ps1 | iex"
```

Preparação reproduzível e validação completa da Etapa 1:

```powershell
uv sync --locked
.\scripts\quality.ps1
```

O `uv` baixa automaticamente o CPython `3.13.15` fixado em `.python-version`.
Não use `pip install` manual nem regenere o lock implicitamente. Atualizações são
intencionais: altere as versões diretas, execute `uv lock` e valide novamente.

Decisões, comandos individuais, compatibilidade e limites desta etapa estão em
[`docs/ADR-001_Toolchain_Reproduzivel_V0.1.md`](docs/ADR-001_Toolchain_Reproduzivel_V0.1.md).
