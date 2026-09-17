# V0.4-S8 — Evidência de acessibilidade e responsividade

- Data: 17 de setembro de 2026.
- Candidato: V0.4 após S1–S7 e correções S8.
- Resultado: **PASS assistido**, com limitações explícitas; não constitui
  declaração de conformidade WCAG integral.

## Ambiente e método

- Auditoria automatizável: testes Django, inspeção do DOM e árvore de
  acessibilidade do navegador.
- Auditoria assistida: Brave baseado em Chromium, único navegador disponível
  na automação. Chrome e Edge foram tentados e reportados como indisponíveis;
  a versão exata do Brave não foi exposta pela ferramenta.
- Viewport normal observado: 1536 x 735 CSS px, DPR 1,25.
- Viewport móvel observado: 360 x 800 CSS px, DPR 1.
- Reflow equivalente a 200% em uma tela de 1536 px: viewport de 768 x 735 CSS
  px. O controle não expôs o zoom nativo do browser; portanto esta evidência é
  de equivalência de reflow, não uma afirmação de acionamento do zoom nativo.
- Leitor de tela não foi executado. A árvore de acessibilidade foi inspecionada,
  mas não substitui teste com tecnologia assistiva real.

## Resultados observados

- Dashboard, consulta/filtros/paginação, detalhe, timeline e fila de revisões
  preservaram headings, links, listas, formulários e landmarks coerentes.
- A tecla `Tab` iniciou pelo skip link, percorreu navegação, breadcrumb,
  filtros e ações em ordem lógica; o foco foi visível. `Enter` ativou o skip
  link, a busca e o detalhe. Não houve keyboard trap no percurso observado.
- O skip link transferiu foco para `#conteudo-principal`, com contorno visível.
- Os oito controles da consulta possuíam labels explícitos; mensagens e estados
  observados usaram texto, não apenas cor.
- Em 360 px, dashboard, consulta, detalhe, timeline e fila não apresentaram
  overflow horizontal no documento nem controles fora do viewport. As tabelas
  largas ficaram contidas em wrappers com `overflow-x: auto`.
- Em 768 px, dashboard, consulta, detalhe e fila também ficaram sem overflow do
  documento, sobreposição ou controles inacessíveis.
- Empty states e métricas sem denominador foram revalidados por regressão: a UI
  mantém “Sem dados”/mensagens recuperáveis e não converte indisponibilidade em
  `0%` ou sucesso.

## Contraste objetivo

Razões calculadas a partir dos tokens CSS usados nas superfícies auditadas:

| Par | Razão |
| --- | ---: |
| texto / fundo | 15,16:1 |
| texto / superfície | 16,27:1 |
| texto secundário / superfície | 7,54:1 |
| texto secundário / fundo | 7,02:1 |
| primária / superfície | 7,85:1 |
| primária / aviso | 7,11:1 |
| branco / primária | 7,85:1 |
| foco / superfície | 5,98:1 |
| foco / fundo | 5,58:1 |
| sucesso / superfície | 7,48:1 |
| sucesso / fundo de sucesso | 6,71:1 |
| erro / superfície | 8,89:1 |
| erro / fundo de erro | 8,04:1 |

## Defeitos corrigidos e revalidados

1. As tabelas de desempenho não tinham nome acessível próprio. Foram ligadas
   aos títulos das seções por `aria-labelledby`; a árvore passou a anunciá-las
   como “Desempenho por disciplina” e “Desempenho por assunto”.
2. O link lista → detalhe perdia o contexto da consulta. O retorno agora inclui
   caminho local, parâmetros GET permitidos e página normalizada; destinos
   externos e parâmetros desconhecidos continuam rejeitados.
3. Fila, timeline e correção de diagnóstico introduziam `<main>` aninhado no
   landmark global. Os wrappers redundantes foram removidos; cada página passou
   a possuir exatamente um `main`.

Os testes de regressão afetados passaram, e o gate final confirmou 327 testes,
88% de cobertura e todos os controles de segurança/qualidade GREEN.
