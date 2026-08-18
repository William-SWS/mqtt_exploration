# Integrar os oito modelos tradicionais

## What to build

Criar um registry declarativo e ampliar o caminho OOF para LDA, QDA, GaussianNB, SVC, Decision Tree, Random Forest, Gradient Boosting e Logistic Regression. Cada factory deve declarar suporte a probabilidade, escala, esparsidade e estratégia cost-sensitive, preservando warnings e falhas como resultados consultáveis.

## What to study

- Premissas, fronteiras e limitações numéricas das oito famílias.
- Clonagem de estimadores, factories sem estado e capability metadata.
- Diferença entre `predict_proba`, `decision_function` e calibração posterior.
- Tratamento de warnings, singularidade e falhas esperadas sem viés de sobrevivência.

## Recommended tools and libraries

- scikit-learn para todos os oito estimadores e clonagem.
- Python `warnings`, logging estruturado e dataclasses ou modelos validados para capabilities.
- Joblib para persistência dos baselines concluídos.
- pytest parametrizado sobre o registry e combinações de regime.

## Acceptance criteria

- [ ] Registry contém exatamente oito nomes únicos e retorna instâncias independentes.
- [ ] Cada modelo declara como produz scores/probabilidades e recebe custo.
- [ ] Os oito modelos executam pelo mesmo runner e produzem schema de artefatos idêntico.
- [ ] Seeds e parâmetros efetivos aparecem no manifesto.
- [ ] Warnings numéricos são capturados sem serem silenciados globalmente.
- [ ] Combinação inviável permanece como `failed` com tipo, mensagem e duração.
- [ ] Nenhuma execução acessa o holdout.

## Blocked by

- {{ISSUE_06}}
- {{ISSUE_07}}

## User stories covered

46–49 e 65.
