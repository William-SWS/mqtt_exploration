# Task 07 — Seleção de features dentro dos folds

## Objetivo

Comparar sete variantes de seleção sem criar datasets globais selecionados e sem permitir que labels de validação influenciem máscaras.

## Pré-requisitos

- Concluir a Task 06 e ler ADR-009 e ADR-010.
- Ter pipelines que expõem nomes das features transformadas.
- Entender filtro, wrapper/embedded, regularização e importância de árvores.

## Conceitos e APIs para estudar

- `VarianceThreshold` e `SelectKBest` com `f_classif` e `mutual_info_classif`.
- Lasso como regressão L1 usada para ranking/seleção, separada de Logistic Regression L1.
- `SelectFromModel` com Logistic Regression L1, `LinearSVC` e `ExtraTreesClassifier`.
- CV interna de três folds para parâmetros do seletor, fitted attributes e máscaras.

## Exercício a implementar futuramente

Criar um registry com sete seletores: variância; ANOVA F; informação mútua; Lasso; logística L1; LinearSVC L1; ExtraTrees. Somar o caminho `none` para formar oito caminhos. Encapsular seleção no pipeline, ajustar apenas no treino externo e, quando houver parâmetros, usar três folds internos agrupados. Salvar máscara, nomes e frequência por fold.

## Entregáveis

- Registry de sete seletores e caminho baseline explícito.
- Espaços de busca internos e regra para número mínimo/máximo de features.
- Artefatos por fold com máscara, nomes, scores/importâncias e estabilidade.
- Relatório de compatibilidade seletor × pré-processamento × modelo.

## Testes esperados

- Exatamente oito caminhos de features estão disponíveis.
- “Lasso” e “Logística L1” são factories e resultados distintos.
- Labels da validação externa nunca chegam ao `fit` do seletor.
- Máscara e `get_feature_names_out` têm o mesmo comprimento e ordem.
- Seleção vazia ou incompatível vira `failed` com motivo reproduzível.

## Critérios de aceite

- Nenhum CSV selecionado global é gerado.
- Todo artefato de seleção identifica fold, dados de treino e hiperparâmetros.
- Frequência de seleção é agregada sem refazer fit nos dados completos.
- O melhor seletor será escolhido por modelo, não imposto globalmente.

## Perguntas de reflexão

- Por que estabilidade de seleção pode importar além do Macro-F1?
- Lasso para alvo binário é um modelo de probabilidade ou apenas um seletor nesta trilha?
- Como comparar importâncias quando o one-hot expande uma feature original?

## Decisões que devem ser registradas

Registrar implementação exata do Lasso, thresholds/espaços, CV interna, agrupamento de one-hot para relato e tratamento de seleção vazia.
