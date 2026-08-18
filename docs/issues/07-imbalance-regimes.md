# Adicionar os três regimes de desbalanceamento

## What to build

Expandir o baseline OOF para executar as receitas original, cost-sensitive e SMOTENC como configurações mutuamente exclusivas. Cada receita deve atravessar o mesmo runner, folds, métricas e manifests, declarando como o estimador recebe custo e demonstrando que reamostragem ocorre somente no treino.

## What to study

- Desbalanceamento, alteração de prior, custo de erro e oversampling sintético.
- `class_weight`, `sample_weight`, priors e `pos_weight`; diferenças de semântica.
- SMOTENC para dados mistos e posicionamento relativo a imputação/encoding.
- Armadilhas de reamostrar o dataset antes da cross-validation.

## Recommended tools and libraries

- imbalanced-learn `Pipeline` e `SMOTENC` para reamostragem dentro dos folds.
- scikit-learn para pipelines e pesos de modelos tradicionais.
- pandas/NumPy para validação das categorias e prevalências.
- pytest parametrizado por regime e capacidade do estimador.

## Acceptance criteria

- [ ] As três receitas são selecionáveis pela configuração e têm identidades distintas.
- [ ] Regime original não altera amostras nem aplica custo.
- [ ] Cost-sensitive calcula pesos/priors somente a partir do treino do fold.
- [ ] SMOTENC chama `fit_resample` apenas no treino, mantém categorias válidas e atinge a razão configurada.
- [ ] SMOTENC e pesos jamais coexistem na mesma execução.
- [ ] Modelos sem uma forma de custo suportada falham antes do treinamento com explicação.
- [ ] Relatórios por fold mostram distribuição antes/depois sem persistir dataset sintético global.

## Blocked by

- {{ISSUE_06}}

## User stories covered

41–45.
