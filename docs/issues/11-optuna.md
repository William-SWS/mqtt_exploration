# Otimizar os oito finalistas tradicionais com Optuna

## What to build

Adicionar um estágio de tuning que crie um estudo persistente por modelo para o seletor/regime vencedor, execute cinco folds agrupados dentro do objetivo e use 30 trials TPE com seed. Espaços serão específicos e condicionais; métricas por fold, estados e melhores parâmetros deverão ser exportados sem tocar no holdout.

## What to study

- Otimização bayesiana TPE, exploração/explotação e orçamento comparável.
- Espaços condicionais, pruning, trials falhos e risco de otimizar ruído de CV.
- Storage persistente, identidade de estudo, retomada e concorrência.
- Nested CV e isolamento completo de cada avaliação.

## Recommended tools and libraries

- Optuna com `create_study`, `TPESampler(seed=...)` e storage SQLite.
- scikit-learn para folds e pipelines clonados por trial.
- pandas para exportar trials e diagnósticos.
- pytest com estudos pequenos em diretórios temporários para retomada e ramos condicionais.

## Acceptance criteria

- [ ] Há um estudo de identidade única para cada um dos oito modelos.
- [ ] Cada objetivo refaz todo fit em cinco folds agrupados de desenvolvimento.
- [ ] Cada estudo contabiliza 30 trials segundo a política documentada de completo/podado/falho.
- [ ] Ramos inativos não registram parâmetros condicionais inválidos.
- [ ] `load_if_exists` só retoma estudo com identidade/configuração compatível.
- [ ] Melhor trial é escolhido por Macro-F1 e exporta recall, log loss e scores por fold.
- [ ] O holdout permanece fechado durante todos os trials.

## Blocked by

- {{ISSUE_10}}

## User stories covered

66–70.
