# Task 09 — Otimização com Optuna

## Objetivo

Otimizar, com orçamento igual e estudos persistentes, o melhor seletor/regime de cada família sem contaminar o holdout.

## Pré-requisitos

- Concluir a Task 08 e ler ADR-012 e ADR-016.
- Congelar um vencedor de screening por cada um dos oito modelos.
- Entender nested CV, espaço condicional e risco de sobreajuste ao protocolo.

## Conceitos e APIs para estudar

- `optuna.create_study`, `TPESampler(seed=...)`, `direction="maximize"`.
- Storage SQLite, `study_name`, `load_if_exists=True` e retomada.
- `trial.suggest_float/int/categorical`, ramos condicionais e atributos de trial.
- `Study.optimize(..., n_trials=30, catch=...)`, pruning versus falha e CV dentro do objetivo.

## Exercício a implementar futuramente

Criar um estudo persistente por modelo, com nome derivado da identidade experimental. O objetivo executará cinco folds agrupados e retornará Macro-F1 médio; salvará recall/log loss e resultados por fold como atributos. Usar espaços específicos e condicionais, 30 trials, seed comum e tratamento explícito de erros esperados. Não alterar seletor/regime vencedor durante o estudo.

## Entregáveis

- Oito bancos/estudos persistentes e exportação tabular dos trials.
- Definição versionada dos espaços de busca.
- Melhor conjunto de hiperparâmetros e evidência por fold de cada modelo.
- Manifesto que distingue trials completos, podados e falhos.

## Testes esperados

- Retomar o mesmo estudo não duplica trials já concluídos nem muda identidade.
- Cada modelo atinge 30 trials contabilizados segundo política registrada.
- A função objetivo usa somente folds de desenvolvimento e refaz todo fit por fold.
- Espaços condicionais não registram parâmetros de ramos inativos.
- Seed do sampler e parâmetros efetivos aparecem no manifesto.

## Critérios de aceite

- Oito finalistas tradicionais são congelados antes de qualquer teste final.
- Orçamento é igual, salvo falha documentada e não recuperável.
- Melhor trial é escolhido por Macro-F1; desempates seguem a política global.
- Holdout continua fechado.

## Perguntas de reflexão

- Trinta trials medem igualmente espaços de dimensões muito diferentes?
- Quando `load_if_exists` pode retomar acidentalmente um estudo incompatível?
- Pruning em folds parciais pode favorecer modelos mais instáveis?

## Decisões que devem ser registradas

Registrar versão Optuna, storage, seed, nomes dos estudos, espaços, exceções capturáveis, política de pruning, oito melhores trials e hashes dos estudos exportados.
