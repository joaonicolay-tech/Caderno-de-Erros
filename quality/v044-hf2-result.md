# V0.4.4-HF2 - evidência de encerramento

- A clarificação autorizada foi registrada: a Fila recebe uma representação de no máximo 500 caracteres, sem alterar o enunciado persistido.
- Reprodução pré-correção: o template renderizava `revision.stem` integral e o teste UX2 só verificava classe/CSS. A regra `.review-queue-item h3 a { display: inline-block; }` tinha maior especificidade que `.review-queue-stem { display: -webkit-box; }`, anulando o clamp nos links atrasados/de hoje.
- Correção: `truncatechars:500` no template produz a representação determinística; o clamp de duas linhas continua como proteção visual secundária. Stems até 500 ficam intactos e os maiores terminam em reticência dentro do total de 500.
- Testes focados: 30 PASS em `test_stage4_learning.py`, `test_dashboard.py` e `test_interface.py`; cobrem texto curto/limite/longo, revisão integral, CTA atrasada/hoje/futuras/ordem, dashboard, Workspace e N+1. `makemigrations --check --dry-run`: sem mudanças.
- Browser SQLite isolado: stem de ~1.500 resumido com reticência em desktop e 360 px, sem overflow; revisão aberta contém o stem integral. CTA apontou para atrasada, depois para hoje quando a atrasada virou futura, e desapareceu quando só restaram futuras. Servidor, banco e auxiliar isolados foram removidos. Zoom 200% não foi mensurável pela automação e não é declarado PASS.
- A8 padrão: **APPROVED**, sem Blocker/Major. `git diff --check`: PASS. Os dois primeiros gates encontraram formatação e ordenação de import, corrigidas no escopo; a passagem seguinte foi inconclusiva apenas por `pip-audit` WinError 10013. A repetição autorizada com rede: **GREEN**, exit 0, 338 testes, 88% cobertura, sem vulnerabilidades, 125,8 s.

Não houve migration, mudança de policy/scheduling/analytics, tag, commit, push, release ou V0.5. `v0.4.3` foi somente consultada e `v0.4.4` não foi criada.
