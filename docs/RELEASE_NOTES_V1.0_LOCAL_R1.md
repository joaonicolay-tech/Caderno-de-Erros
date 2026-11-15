# V1.0 Local r1 — notas da distribuição de fonte

Aplicação 1.0.0, rota V1.0_LOCAL_R1; CEI-EXPORT-1.0 permanece inalterado.
Identificação da versão: v1.0.0, V1.0 Local r1. Canal: fonte reproduzível com testes e preparação sintética,
sem instalador universal ou ativação pública para dados pessoais.

## Proveniência e mudanças

Derivação do candidato v014, identidade
`fb940bdc2903e2ea4e8875c297ef20c1737cfa7e85f4c505a4601761e0794b3c`.
O ZIP privado aprovado permanece com SHA-256
`84b4265b51938c330fed5d0132b3b2a25c26a7512a6281b732fd9f4868c31be6`;
não é o ZIP público de fonte e não será anunciado como instalador geral.

Inclui fronteira SQLite/paths, importação histórica bloqueada, ativação privada
sem relaxamento, exportação e backup/restore/recovery, identidade visual Local r1
e testes do candidato. Nenhuma migration foi alterada ou adicionada. O lock
integra certifi 2026.10.19, filelock 4.2.1 e msgpack 1.2.3 do candidato.

A derivação pública remove caminhos pessoais fixos, resolve a raiz pelo layout
da instância e separa build/verificação de fonte dos gates privados de aceite.
Não inclui .local-r1.json, banco, segredo, autorização, backups ou evidence.
A seleção e os hashes originais estão em quality/source-baseline.json.

## Suporte e limites

- Windows 11 x64, C: local, Python 3.13.15, uv 0.12.7, Django 5.2.17.
- Chrome desktop; observação humana anterior na versão 157.0.8103.39, com seu
  alcance individual. Edge não qualificado. Brave histórico não qualifica esta
  derivação. Não há suporte mobile, remoto ou multiusuário.
- CT-126: DEFERRED_BY_OWNER_V1_0_NOT_QUALIFIED. Sem PASS nem defeito comprovado
  inferido. Não foi aberta nova rodada humana nesta preparação.
- Quatro LIMITED temporais REV-004/TIMEZONE_CONTEXT_UNAVAILABLE preservados;
  não se afirma espera real D7/D14/D30 ou meses de uso.
- BCR-1/BCR-2 são evidências sintéticas anteriores; excedências brutas do perfil
  2x permanecem. Esta integração não cria SLA ou novo benchmark de uso real.
- Recuperação qualificada anteriormente no modelo de processo próprio;
  dispositivo único e cadência manual de backup. Não demonstra perda de disco,
  energia ou host, nem substitui segunda mídia verificada.
- A8 histórica CHANGES_REQUIRED, F01/F02/F03, HD-01/02, STOPs e retenção histórica
  permanecem nos seus escopos. Fonte pública não encerra esses resultados.

O pacote público permite regressão/demonstração sintéticas. Qualificação privada
por instalação e liberação para novos dados reais não são provisionadas aqui.
Importação CEI e migração de acervo antigo seguem bloqueadas na rota Local r1.

Consulte [reprodução da fonte](V1.0_Local_r1_Fonte.md),
[instalação](V1.0_Local_r1_Instalacao.md) e
[operação](V1.0_Local_r1_Operacao.md). Não foi escolhida uma licença de projeto
nesta preparação; a licença distribuída do htmx permanece preservada.

## Depois da V1.0

Prioridades atuais: melhorar a interface visual e simplificar a inicialização.
Não fazem parte desta integração. Depois dessas melhorias, o responsável
solicitou uma auditoria completa do GitHub. O backlog pós-V1 existente mantém
calibração, Markdown/LaTeX, FTS, API/exportadores, revisão adaptativa,
hospedagem/PostgreSQL e IA assistiva condicionados a evidência e escopo próprio.
