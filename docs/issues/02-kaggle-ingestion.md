# Adquirir e validar o dataset versionado do Kaggle

## What to build

Adicionar ao runner um estágio de aquisição que receba um handle Kaggle versionado, baixe os três CSVs, valide nomes e SHA-256 e produza um manifesto de proveniência. O estágio deve reutilizar download válido, rejeitar versão implícita e nunca registrar credenciais. Incluir a checklist operacional para criar o espelho privado e verificar uma nova versão antes de torná-la pública.

## What to study

- Autenticação Kaggle, dataset metadata, licença CC BY 4.0 e versionamento imutável.
- Diferença entre cache, integridade de transporte e integridade verificada localmente.
- SHA-256 streaming, atomicidade de download e tratamento de arquivos parciais.
- Atribuição, DOI e diferença entre licença do dataset e licença do código.

## Recommended tools and libraries

- Kaggle CLI para `datasets init`, criação privada, status e versionamento.
- KaggleHub para download por `owner/slug/versions/N`.
- `hashlib`, `pathlib` e biblioteca padrão para validação e movimentação atômica.
- pytest `monkeypatch` e `tmp_path` para simular autenticação, cache e corrupção.

## Acceptance criteria

- [ ] Handles sem `/versions/N` são rejeitados antes do download.
- [ ] `Intrusion.csv`, `DoS.csv` e `MitM.csv` são exigidos sem renomeação silenciosa.
- [ ] Hash divergente ou arquivo ausente interrompe o estágio e deixa status `failed` explicativo.
- [ ] Download válido pode ser retomado sem duplicar dados ou manifestos.
- [ ] O manifesto registra owner/slug, versão, DOI, licença, autores, tamanho e hashes.
- [ ] Nenhum token, arquivo de autenticação ou valor secreto aparece em log, manifesto ou Git.
- [ ] A checklist mantém o dataset privado até revisão manual de atribuição e integridade.

## Blocked by

- {{ISSUE_01}}

## User stories covered

10–15, 30, 64 e 103–104.
