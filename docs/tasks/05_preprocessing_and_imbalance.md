# Task 05 — Pré-processamento e desbalanceamento

## Objetivo

Construir pipelines leakage-safe para features numéricas/categóricas e comparar três regimes de classe sem combinar indevidamente reamostragem e pesos.

## Pré-requisitos

- Concluir a Task 04 e ler ADR-009 e ADR-010.
- Ter listas de features por tipo e folds congelados.
- Entender imputação, encoding, scaling, pesos e geração sintética.

## Conceitos e APIs para estudar

- `ColumnTransformer`, `Pipeline`, imputadores, encoders, scalers e `get_feature_names_out`.
- Pipeline do imbalanced-learn e `SMOTENC`, ajustado somente no treino do fold.
- `class_weight="balanced"`, `sample_weight`, priors 0,5/0,5 e `pos_weight`.
- Diferença entre feature categórica antes/depois do encoding e índices esperados pelo SMOTENC.

## Exercício a implementar futuramente

Montar um pré-processador que preserve nomes estáveis e três receitas mutuamente exclusivas: `original`; `cost_sensitive`; e `smotenc`. No regime cost-sensitive, usar `class_weight` quando suportado, `sample_weight` no Gradient Boosting, priors iguais em LDA/QDA/GNB e `pos_weight` na MLP. No regime SMOTENC, reamostrar dentro do fold e nunca aplicar pesos de classe.

## Entregáveis

- Fábricas de pipeline por regime e tipo de modelo.
- Mapa explícito de suporte a pesos/priors para cada estimador.
- Relatório por fold antes/depois da reamostragem.
- Lista ordenada de nomes e tipos das features transformadas.

## Testes esperados

- Imputadores, encoders, scaler e SMOTENC recebem somente treino do fold.
- SMOTENC produz categorias válidas e a prevalência configurada.
- `original` não altera o número de amostras; pesos não aparecem em `smotenc`.
- Nomes, ordem e quantidade de features são estáveis entre fit/transform.
- Pesos/prior são calculados somente com labels de treino.

## Critérios de aceite

- Os três regimes têm semântica comparável e manifestos explícitos.
- Nenhuma matriz reamostrada é persistida como dataset global.
- Modelos sem `class_weight` recebem a alternativa decidida ou falham cedo.
- Transformar validação nunca chama `fit` ou `fit_resample`.

## Perguntas de reflexão

- Por que SMOTENC deve ocorrer antes do one-hot encoding na receita escolhida?
- Pesos “balanced” mudam probabilidades ou apenas a fronteira de decisão?
- Como detectar que uma categoria sintética inválida foi criada?

## Decisões que devem ser registradas

Registrar imputadores, encoding, scaling, estratégia do SMOTENC, razão alvo, mapa de pesos/priors e convenção de nomes de features.
