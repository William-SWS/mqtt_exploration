# Integrar os oito caminhos de features

## What to build

Criar um registry com sete seletores e um caminho explícito sem seleção, integrando-os ao pipeline OOF. Seletores supervisionados e seus parâmetros devem ser ajustados exclusivamente no treino externo, usando três folds internos agrupados quando necessário. Cada fold deve publicar máscara, nomes, scores/importâncias e frequência agregável.

## What to study

- Métodos filter e embedded; estabilidade e viés de seleção.
- VarianceThreshold, ANOVA F, mutual information e SelectFromModel.
- Lasso como seletor linear separado de Logistic Regression L1.
- Nested CV, expansão one-hot e mapeamento para features originais.

## Recommended tools and libraries

- scikit-learn para os seletores, LinearSVC, Logistic Regression e ExtraTrees.
- pandas/NumPy para máscaras, nomes e frequência por fold.
- O pipeline existente para manter seleção dentro da fronteira de validação.
- pytest com labels sentinela e casos de seleção vazia/incompatível.

## Acceptance criteria

- [ ] Existem exatamente oito caminhos: `none` mais sete seletores.
- [ ] Lasso e Logistic Regression L1 têm factories, parâmetros e artefatos distintos.
- [ ] Labels da validação externa nunca chegam ao `fit` ou à CV interna do seletor.
- [ ] Máscara, scores e nomes têm comprimento e ordem consistentes.
- [ ] Três folds internos respeitam grupos e usam apenas o treino externo.
- [ ] Seleção vazia ou matriz incompatível produz registro `failed`, não desaparecimento.
- [ ] Nenhum CSV global de features selecionadas é criado.

## Blocked by

- {{ISSUE_06}}
- {{ISSUE_07}}

## User stories covered

50–55.
