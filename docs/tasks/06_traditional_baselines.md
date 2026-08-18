# Task 06 — Baselines tradicionais

## Objetivo

Definir oito famílias de modelo por registry e produzir baselines honestos, sem seleção de features e sem tuning oportunista.

## Pré-requisitos

- Concluir a Task 05 e ler ADR-010 e ADR-011.
- Ter métricas binárias definidas com `intrusion` como classe positiva.
- Entender diferenças entre margem, probabilidade e decisão de classe.

## Conceitos e APIs para estudar

- LDA, QDA, GaussianNB, SVC, Decision Tree, Random Forest, Gradient Boosting e Logistic Regression.
- Hiperparâmetros baseline, `random_state`, suporte a `predict_proba` e limitações numéricas.
- Registry `name -> factory`, clonagem de estimadores e capacidades declarativas.
- Macro-F1, recall da intrusão e log loss como sinais diferentes.

## Exercício a implementar futuramente

Criar um registry para os oito modelos, com factories sem estado e metadata de suporte a pesos, escala, esparsidade e probabilidades. Executar a configuração baseline sem seletor nos três regimes sobre folds de desenvolvimento, preservando warnings e falhas. Não escolher vencedor ainda.

## Entregáveis

- Registry único dos oito modelos e testes de construção.
- Tabela baseline por fold/configuração, com status e duração.
- Manifestos com defaults efetivos, seed e versões.
- Relatório de warnings numéricos, sobretudo para QDA.

## Testes esperados

- Registry contém exatamente oito nomes únicos e retorna instâncias novas.
- Todo modelo declara como produz score/probabilidade e como recebe custo.
- Mesma seed reproduz resultados dentro da tolerância definida.
- Falha numérica cria registro `failed` com tipo/mensagem, sem sumir da tabela.

## Critérios de aceite

- Defaults e pequenas adaptações necessárias estão documentados antes da execução.
- Não há condicionais de modelo espalhadas pelo runner.
- Baseline usa o mesmo split e métrica para todas as famílias.
- Não há acesso ao holdout nem ajuste de hiperparâmetro nesta tarefa.

## Perguntas de reflexão

- Quando `probability=True` do SVC altera custo e semântica da comparação?
- Por que QDA pode falhar após encoding/seleção?
- Um modelo com ótimo Macro-F1 e log loss ruim serve para ensemble probabilístico?

## Decisões que devem ser registradas

Registrar estimadores exatos, defaults alterados, seed, política para probabilidades, warnings tolerados e critérios para marcar uma execução como falha.
