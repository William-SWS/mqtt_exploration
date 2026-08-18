# Executar um baseline OOF end-to-end

## What to build

Entregar o primeiro tracer bullet experimental completo: a partir do cenário validado e dos folds congelados, pré-processar features mistas dentro de cada fold, treinar Logistic Regression no regime original sem seletor, gerar probabilidades OOF alinhadas, calcular o conjunto inicial de métricas e salvar modelo, predições e manifesto retomável.

## What to study

- `ColumnTransformer`, `Pipeline`, imputação, one-hot encoding e scaling sem vazamento.
- Probabilidade versus classe, OOF e alinhamento por índice.
- Macro-F1, recall da intrusão, PR-AUC, ROC-AUC, FPR e log loss.
- Persistência segura de estimadores e identidade de execução.

## Recommended tools and libraries

- scikit-learn para pipeline, Logistic Regression e métricas.
- pandas/NumPy para alinhamento e tabelas OOF.
- Joblib para o artefato sklearn acompanhado de metadata.
- pytest com estimadores sentinela para provar a fronteira `fit/transform`.

## Acceptance criteria

- [ ] Imputadores, encoder, scaler e estimador veem somente o treino de cada fold durante `fit`.
- [ ] Existe exatamente uma probabilidade OOF finita em `[0,1]` por linha de desenvolvimento.
- [ ] Nomes e ordem de features permanecem estáveis entre treino e transformação.
- [ ] Métricas conferem com exemplos pequenos calculados independentemente.
- [ ] Manifesto registra split, regime, caminho de features, modelo, seed, versões, duração e status.
- [ ] `--resume` reutiliza execução completa compatível e rejeita identidade incompatível.
- [ ] O holdout não é aberto.

## Blocked by

- {{ISSUE_05}}

## User stories covered

38–40, parte de 46–49 e 59–64.
