# Task 01 — Kaggle, proveniência e integridade

## Objetivo

Criar futuramente um espelho Kaggle pessoal, versionado e verificável dos três CSVs, preservando atribuição, licença e integridade sem expor credenciais.

## Pré-requisitos

- Concluir a Task 00 e ler ADR-005.
- Confirmar no Figshare autores, título, DOI e licença CC BY 4.0.
- Ter uma conta Kaggle pessoal e permissão para redistribuir os arquivos segundo a licença.

## Conceitos e APIs para estudar

- Proveniência, SHA-256, versionamento imutável e cadeia de custódia dos dados.
- `kaggle auth login`, `KAGGLE_API_TOKEN` e armazenamento externo de tokens.
- `kaggle datasets init -p`, `create`, `status`, `version` e download para verificação.
- Campos de `dataset-metadata.json`, slug `owner/dataset-slug` e licença `CC-BY-4.0`.
- `kagglehub.dataset_download("owner/slug/versions/N")`; cache padrão, `output_dir` e `force_download`.

## Exercício a implementar futuramente

1. Recalcular os hashes dos três CSVs e conferir autores, DOI e licença.
2. Autenticar sem criar segredo versionado.
3. Em uma pasta temporária, copiar os CSVs e gerar `dataset-metadata.json` com `kaggle datasets init`.
4. Preencher slug pessoal, título, descrição, fonte e `CC-BY-4.0`.
5. Criar o dataset sem `--public` (privado por padrão) e consultar `kaggle datasets status owner/slug`.
6. Baixar novamente, conferir nomes, tamanhos e hashes e só então considerar publicação manual.
7. Para mudanças, usar `kaggle datasets version`; nunca apagar versões anteriores.
8. Fixar `owner/slug/versions/N` no cenário do pipeline e validar hashes após `dataset_download`.

## Entregáveis

- Registro de proveniência com autores, DOI, licença, versão Kaggle e hashes.
- Checklist preenchida para revisão antes de tornar o dataset público.
- Handle versionado e instruções de recuperação reproduzível.

## Testes esperados

- Os três hashes baixados são idênticos aos hashes aprovados.
- Falta de autenticação e hash divergente produzem erro claro e interrompem o fluxo.
- Busca por segredos no Git não encontra token, `.env`, `kaggle.json` ou access token.
- O handle sem `/versions/N` é rejeitado pela configuração reprodutível.

## Critérios de aceite

- O dataset nasce privado e só é publicado após atribuição e integridade revisadas.
- `Intrusion.csv`, `DoS.csv` e `MitM.csv` estão presentes, sem renomeação silenciosa.
- DOI e licença aparecem no metadata e na descrição.
- A versão e os hashes são suficientes para reconstruir exatamente a entrada.

## Perguntas de reflexão

- Por que o cache do KaggleHub não substitui nossa validação de hash?
- Que diferença existe entre licença dos dados e licença do código deste repositório?
- Que mudança justificaria uma nova versão Kaggle?

## Decisões que devem ser registradas

Registrar owner/slug, versão publicada, data, hashes, autores/licença confirmados, método de autenticação, checklist de publicidade e qualquer divergência da cópia Figshare.
