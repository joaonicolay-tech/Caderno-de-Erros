# ADR-006 — Interface acessível da fundação V0.1

- **Status:** Aceita
- **Data:** 2026-09-02
- **Escopo:** Etapa 6 da V0.1
- **Resolve:** `SDD-ABR-002`
- **Requisitos:** `RF-001`–`RF-003`; `RN-001`–`RN-005`; `RNF-009`, `RNF-010`,
  `RNF-044`–`RNF-049`, `RNF-063`, `RNF-065`, `RNF-066`
- **Fluxo:** `FL-023`
- **Testes:** `CT-002`, `CT-136` e parcela estrutural aplicável de `CT-128`

## Decisão

A apresentação mínima usa Django Templates, formulários Django, HTML semântico e
CSS próprio versionado. Não há framework CSS, biblioteca de componentes, Node.js,
bundler ou JavaScript de aplicação. Esta é a alternativa mais simples que mantém
validação no servidor, CSRF e respostas completas, conforme `SDD-ADR-009`.

O HTMX 2.0.10 foi armazenado localmente em
`src/static/vendor/htmx-2.0.10.min.js`, acompanhado de sua licença. Um teste
recalcula e exige o SRI congelado no ADR-001. Como os dois formulários desta etapa
não ganham simplicidade ou acessibilidade com atualização parcial, o artefato não
é carregado no template nem são criados atributos `hx-*`. Ele fica disponível
para uma interação documentalmente necessária em etapa futura.

O artefato foi obtido da distribuição `htmx.org@2.0.10`; versão e SRI foram
conferidos com a documentação oficial:
<https://github.com/bigskysoftware/htmx/blob/master/www/content/docs.md>.

## Rotas e estados

- `/`: redireciona para primeiro acesso enquanto não existir Workspace; depois
  apresenta somente estado real da fundação e acesso às configurações;
- `/primeiro-acesso/`: escolhe explicitamente um fuso IANA e executa o bootstrap
  idempotente de User, Workspace e dez categorias;
- `/configuracoes/`: mostra o fuso atual e permite confirmar ou cancelar uma
  alteração protegida por `lock_version`;
- `/health/`: permanece o diagnóstico técnico definido no ADR-005.

Não há links, telas ou estados simulados para questões, revisões, dashboard,
busca, métricas, domínio ou categorias pessoais.

## Feedback e concorrência

O padrão Post/Redirect/Get fornece feedback textual de sucesso, cancelamento e
estado inalterado. Erros de campo permanecem junto ao controle. Falha técnica não
anuncia sucesso. Conflito de `lock_version` recarrega o valor atual e exige nova
confirmação, sem reaplicar automaticamente a intenção anterior.

As views recebem o Workspace local pelos IDs técnicos mantidos no servidor; não
aceitam IDs de usuário ou Workspace do formulário. Regras de bootstrap, fuso e
concorrência continuam nos serviços existentes. A correlação HTTP do ADR-005
alcança esses serviços sem registrar valores do formulário.

## Baseline de acessibilidade e responsividade

- `lang="pt-BR"`, UTF-8 e viewport responsivo;
- regiões nativas `header`, `nav`, `main`, `section` e `footer`;
- link de salto e hierarquia única de títulos por página;
- labels persistentes e ajuda/erros associados por `aria-describedby`;
- `aria-invalid`, foco no primeiro erro e região textual de feedback;
- links, botões, select e checkbox nativos, sem ordem positiva de `tabindex`;
- foco visível, alvos mínimos, estados com texto e borda além de cor;
- cores principais com contraste textual mínimo de 4,5:1 verificado em teste;
- layout fluido, quebra de conteúdo e controles utilizáveis entre 360 e 1920 px
  e com zoom de 200%, sem depender de rolagem horizontal para texto principal.

O smoke visual aplicável usa Chrome e Edge nas versões de referência congeladas
no ADR-001. Automação de navegador não é adicionada à toolchain nesta etapa.

Na execução da Etapa 6, o ambiente não disponibilizou navegador controlável. A
evidência automatizada aplicável ficou restrita a renderização funcional,
semântica, foco, contraste, viewport e regras responsivas. O percurso visual real
em Chrome/Edge permanece no gate completo de `CT-128`, cuja fase autoritativa é
V0.4/V1; isso não introduz infraestrutura de navegador na V0.1.

No perfil `production_local`, o comando documentado usa `runserver --insecure`
exclusivamente para servir os assets versionados com `DEBUG=False` na aplicação
loopback. Isso não autoriza exposição remota nem substitui uma estratégia de
servidor estático para uma implantação futura.

## Itens deliberadamente adiados

Backup/restauração, conteúdo de estudo, questões, tentativas, ciclos, revisões,
dashboard, busca, métricas, categorias pessoais, autenticação remota, notificações,
PWA, API e navegação correspondente permanecem nas etapas próprias. O uso runtime
de HTMX será introduzido somente quando uma interação real justificar progressão.
