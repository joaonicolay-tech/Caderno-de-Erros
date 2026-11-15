# Caderno de Erros — V1.0 Local r1

Aplicação Django em português para uso individual local no Windows 11 x64:
questões e tentativas, categorias de erro, revisões D1/D7/D14/D30, histórico,
domínio/prioridade explicáveis, pesquisa, dashboard, exportação CEI e
backup/restauração SQLite.

Esta distribuição é **código-fonte reproduzível**, derivado do candidato privado
v014, com uma preparação explícita para verificação **somente sintética**.
Não é instalador universal. A ativação e a qualificação de armazenamento da
instalação privada não são transferidas para um clone, outra pasta ou outro PC.
Não use a preparação sintética para dados pessoais.

- [Reproduzir fonte, ambiente e testes](docs/V1.0_Local_r1_Fonte.md)
- [Operação e limites](docs/V1.0_Local_r1_Operacao.md)
- [Instalação: alcance desta distribuição](docs/V1.0_Local_r1_Instalacao.md)
- [Notas da versão](docs/RELEASE_NOTES_V1.0_LOCAL_R1.md)
- [Contrato CEI-EXPORT-1.0](docs/CEI_EXPORT_1_0.md)

Versão da aplicação: **1.0.0**; rota: **V1.0_LOCAL_R1**. O formato de exportação
permanece CEI-EXPORT-1.0. Importação lógica e migração de acervo histórico
continuam bloqueadas nos entry points Local r1.

O navegador contemplado é **Chrome desktop**, com observação humana registrada
na versão 157.0.8103.39. Edge não qualificado; o PASS histórico do Brave pertence
à rota anterior. Não há suporte mobile, hospedagem pública ou multiusuário remoto.

O build usa uma lista positiva e gera SOURCE-MANIFEST.json com hashes; nenhum
banco, segredo, marcador de instância, autorização privada, backup ou venv é
incluído. O ZIP privado v014 é preservado como outra entrega, com outro hash.
Os arquivos automáticos “Source code” do GitHub incluem também a documentação
histórica do repositório; o ZIP curado descrito no guia é o artefato verificado.

As limitações CT-126 adiada, quatro LIMITED temporais, benchmarks sintéticos,
backup manual e recuperação no modelo de processo próprio permanecem explícitas
nas notas. A preparação pública não demonstra recuperação de perda do dispositivo.

Depois da V1.0, as prioridades são melhorar a interface visual e simplificar a
inicialização, em escopos próprios.
