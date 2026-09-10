# V0.3 E5 - correção de `Origin: null` no POST local

## Estado

Registro técnico de defeito encontrado antes da execução humana de `CT-125`.
Este artefato não executa, preenche ou decide `CT-125`; o caso permanece
**PENDENTE** conforme `quality/v03-ct125-manual-protocol.md` e ADR-012.

## Causa e correção

As views de tentativa inicial e conclusão de revisão enviavam
`Referrer-Policy: no-referrer`. Para um POST de formulário (navegação que não
usa CORS), o algoritmo Fetch serializa o header `Origin` como `null` sob essa
política. `CsrfViewMiddleware` rejeitou corretamente `null`, pois ele não é a
origem do host nem uma origem confiável.

A política local dos formulários passou a ser `same-origin`. Assim, POSTs
normais servidos por `http://127.0.0.1:8000` enviam
`Origin: http://127.0.0.1:8000`; para destinos cross-origin o Origin continua
`null` e o Referer não é enviado. Nenhuma origem foi incluída em
`CSRF_TRUSTED_ORIGINS`, que continua desnecessário para o host da própria
requisição. `CsrfViewMiddleware`, o token e a rejeição de origem externa
permanecem ativos.

`SECURE_REFERRER_POLICY` não é uma configuração nativa do Django; a política
era um header definido explicitamente pelas views. Não há CSP, sandbox ou
redirect cross-origin no fluxo investigado. `ALLOWED_HOSTS` continua limitado a
`127.0.0.1`, `localhost` e `[::1]`. Os testes HTTP com CSRF forçado cobrem
`127.0.0.1:8000` e `localhost:8000`; não substituem a futura sessão humana de
CT-125.
