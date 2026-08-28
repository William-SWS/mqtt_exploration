# Task 08 — Screening experimental

## Objetivo

Executar e auditar a matriz completa de baselines para reduzir candidatos sem apagar combinações difíceis ou superestimar evidência.

## Pré-requisitos

- Concluir a Task 07 e ler ADR-010, ADR-011 e ADR-016.
- Congelar registries, folds, regimes, caminhos de features, métricas e seeds.
- Ter previsão out-of-fold (OOF) e manifests por execução.

## Conceitos e APIs para estudar

- `cross_val_predict` ou loop OOF explícito, alinhamento por índice e agregação por fold.
- `accuracy_score`, precision/F1/recall, `average_precision_score`, `roc_auc_score`, `log_loss` e matriz de confusão.
- False-positive rate, probabilidades finitas e status `pending/running/completed/failed`.
- Identidade de execução, resume idempotente e tabela longa de resultados.

## Exercício a implementar futuramente

Executar 8 modelos × 8 caminhos de features × 3 regimes = 192 configurações baseline. Para cada uma, produzir probabilidades OOF alinhadas, métricas por fold/agregadas, tempo, features e manifesto. Capturar exceções numericamente previstas, especialmente QDA, como `failed` com motivo. Ordenar por Macro-F1 e desempatar por recall e log loss; latência/tamanho só quando mensurados comparavelmente.

## Entregáveis

- Tabela com exatamente 192 registros e colunas de identidade/status.
- Probabilidades OOF dos casos concluídos e logs resumidos das falhas.
- Ranking por modelo e seleção do melhor seletor/regime de cada modelo.
- Relatório de cobertura, duração e integridade do screening.

## Testes esperados

- Produto cartesiano gera exatamente 192 IDs únicos, mesmo com falhas.
- Cada execução concluída tem uma predição OOF por linha de desenvolvimento.
- Métricas batem com pequenos exemplos manuais conhecidos.
- Probabilidades são finitas e estão em `[0,1]`; labels/índices estão alinhados.
- Resume não duplica nem sobrescreve execução incompatível.
- Holdout não é lido.

## Critérios de aceite

- Nenhuma configuração desaparece da tabela.
- A seleção de oito vencedores usa regra predefinida, sem inspeção do teste.
- Métricas obrigatórias disponíveis nesta fase são calculadas consistentemente.
- Manifesto permite reproduzir ou explicar cada linha.

## Perguntas de reflexão

- Uma falha sistemática é evidência sobre o estimador ou sobre o pipeline?
- Como evitar escolher uma configuração por ruído de um único fold?
- Quando latência de treinamento é irrelevante para desempate operacional?

## Decisões que devem ser registradas

Registrar schema da tabela, regra de agregação, tolerâncias, política de exceções, oito vencedores e justificativa de qualquer métrica indisponível.
