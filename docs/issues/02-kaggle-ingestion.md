# Armazenar, adquirir e validar ativos versionados do Kaggle

## What to build

Adicionar ao runner um estágio de aquisição que receba um handle Kaggle versionado,
baixe os três CSVs, valide nomes e SHA-256 e produza um manifesto de proveniência.
O estágio deve reutilizar download válido, rejeitar versão implícita e nunca registrar
credenciais.

Estabelecer também o contrato de persistência remota do projeto: os CSVs brutos
ficam em um Kaggle Dataset privado e versionado; cada artefato de modelo concluído
fica em um Kaggle Model privado, na variação correspondente ao seu framework,
junto do arquivo serializado, manifesto/metadata e hashes. A publicação de uma
nova versão deve conservar as anteriores e registrar o handle versionado que permite
recuperar o ativo em qualquer máquina. As tasks que efetivamente treinam modelos
devem chamar esse contrato após produzir um artefato concluído; esta task entrega a
convenção, a integração e a checklist operacional.

Incluir a checklist operacional para criar ambos os recursos privados, enviar uma
nova versão, recuperá-la por handle fixado e revisar atribuição, integridade e
visibilidade antes de qualquer publicação.

## What to study

- Autenticação Kaggle, metadata de Dataset e Model, licença CC BY 4.0 e
  versionamento imutável.
- Diferença entre cache, integridade de transporte e integridade verificada localmente.
- SHA-256 streaming, atomicidade de download e tratamento de arquivos parciais.
- Atribuição, DOI e diferença entre licença do dataset, licença do modelo e licença
  do código.
- Empacotamento de `joblib`/`state_dict`, metadata e hashes para uma variação de
  Kaggle Model.

## Recommended tools and libraries

- Kaggle CLI para `datasets init`, criação privada, status e versionamento.
- KaggleHub para upload/download de Dataset e Model por handles com versão.
- `hashlib`, `pathlib` e biblioteca padrão para validação e movimentação atômica.
- pytest `monkeypatch` e `tmp_path` para simular autenticação, cache e corrupção.

## Acceptance criteria

- [x] Handles sem `/versions/N` são rejeitados antes do download.
- [x] `Intrusion.csv`, `DoS.csv` e `MitM.csv` são exigidos sem renomeação silenciosa.
- [x] Hash divergente ou arquivo ausente interrompe o estágio e deixa status `failed` explicativo.
- [x] Download válido pode ser retomado sem duplicar dados ou manifestos.
- [x] O manifesto registra owner/slug, versão, DOI, licença, autores, tamanho e hashes.
- [x] Nenhum token, arquivo de autenticação ou valor secreto aparece em log, manifesto ou Git.
- [x] A checklist mantém o dataset privado até revisão manual de atribuição e integridade.
- [x] Todo modelo concluído é empacotado com seu formato serializado, metadata e
  hashes, enviado a um Kaggle Model privado e tem seu handle versionado registrado
  no manifesto local.
- [x] Um modelo salvo pode ser baixado em diretório explicitamente informado por um
  handle `owner/model/framework/variation/N`; handle sem `/N` é rejeitado pelo
  fluxo reproduzível.
- [x] O upload de Dataset ou Model cria uma nova versão sem remover versões
  anteriores, e a checklist mantém ambos privados até revisão manual.

## Blocked by

- [Issue 01 — runner do projeto](01-project-runner.md) (concluída)

## User stories covered

10–15, 30, 64 e 103–104.
