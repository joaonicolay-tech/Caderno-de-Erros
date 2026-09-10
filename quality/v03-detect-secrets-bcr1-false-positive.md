# V0.3 — Registro de falso positivo `detect-secrets` — BCR-1

## Escopo da exceção

A baseline do `detect-secrets` registra exclusivamente a ocorrência
`Hex High Entropy String` em `quality/v03-bcr1-result.json`, linha 41. A
ocorrência é localizada pelo hash interno que o próprio `detect-secrets` usa
para aquele valor e não cria exclusão por arquivo, padrão, detector ou nível de
entropia.

## Justificativa da revisão

O valor é o fingerprint SHA-256 determinístico do manifesto do dataset
sintético BCR-1, construído por `build_dataset_manifest` em
`src/shared/application/bcr1.py`. A entrada do hash contém somente a seed,
contagens autorizadas, IDs UUID estáveis derivados dessas contagens e intervalo
de datas fixo. Não recebe, deriva ou representa senha, token, credencial ou
dado pessoal; sua única finalidade é identificar a composição da evidência do
benchmark de modo reproduzível.

Os detectores, incluindo `HexHighEntropyString` com limite 3.0, permanecem
ativos para todos os demais achados.
