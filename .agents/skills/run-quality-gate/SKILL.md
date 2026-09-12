---
name: run-quality-gate
description: "Execute e interprete o gate de qualidade autoritativo deste repositório. Use para validar uma working tree; não use para redefinir controles ou corrigir falhas fora do escopo."
---

# Executar o gate de qualidade

1. Leia `AGENTS.md`, `tasks/current.md` e a Verification da tarefa autorizada,
   quando houver. Inspecione a working tree e registre quais mudanças estão sob
   avaliação.
2. Execute as verificações prévias exigidas pelo contrato e `git diff --check`.
3. Execute, sem copiar ou substituir sua lógica:

   `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

4. Preserve o resultado observável: comando, exit code, etapa que falhou e
   resumo de testes/cobertura disponível. Não declare GREEN sem exit code 0.
5. Classifique qualquer resultado não aprovado como falha causada pela tarefa,
   falha preexistente, falha ambiental ou resultado inconclusivo, usando apenas
   evidência disponível. Não invente uma causa.
6. Corrija somente quando a tarefa autorizada incluir a correção. Fora do
   escopo, pare e reporte; não altere thresholds, cobertura, testes, migrations,
   detect-secrets, auditoria ou o próprio gate apenas para obter GREEN.

Esta Skill é repetível e independente. Ela executa e interpreta o mecanismo
existente, mas não implementa a tarefa nem autoriza seu encerramento.
