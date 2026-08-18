# Task 04 — Divisão e validação sem vazamento

## Objetivo

Construir um protocolo que simule generalização para o futuro, mantendo o teste final intocado e reduzindo dependência entre treino e validação.

## Pré-requisitos

- Concluir a Task 03 e ler ADR-008 e ADR-009.
- Ter uma ordem temporal confiável preservada separadamente das features do modelo.
- Entender holdout, cross-validation, estratificação, grupos e nested CV.

## Conceitos e APIs para estudar

- Holdout cronológico, índices imutáveis e fronteira temporal.
- `StratifiedGroupKFold(n_splits=5)`, limitações da estratificação com grupos e inspeção por fold.
- Formação de grupos por blocos temporais de 30 s; sensibilidades de 10 s e 60 s.
- CV interna de três folds para hiperparâmetros de seletores; distinção entre validação e teste.

## Exercício a implementar futuramente

Após deduplicar, ordenar e preservar índices, reservar os últimos 30% como holdout. No desenvolvimento inicial (70%), construir grupos de 30 s e materializar apenas a definição dos cinco folds, com contagens, prevalência, intervalos temporais e interseções. Criar uma trava verificável que impeça carregamento de labels/features do holdout durante screening e tuning.

## Entregáveis

- Manifesto da fronteira temporal e dos índices de desenvolvimento/teste.
- Manifesto dos cinco folds e seus grupos.
- Relatório de equilíbrio possível por fold e eventuais limitações.
- Mecanismo de congelamento/desbloqueio auditável do holdout.

## Testes esperados

- Índices de desenvolvimento e teste são disjuntos e cobrem todas as linhas válidas.
- `max(time_dev) <= min(time_test)` sob a regra de empate documentada.
- Nenhum grupo aparece simultaneamente no treino e validação de um fold.
- Cada linha de desenvolvimento aparece uma vez em validação OOF.
- Tentar abrir holdout antes do estado `frozen` falha.

## Critérios de aceite

- Teste contém os últimos 30% segundo uma regra determinística.
- Cinco folds preservam grupos e têm ambas as classes, ou a impossibilidade é registrada.
- Split é reconstruível a partir de configuração, seed e índices.
- Sensibilidades 10/60 s não influenciam o screening; são reservadas aos finalistas.

## Perguntas de reflexão

- Como empates de timestamp na fronteira de 70% devem ser tratados?
- Estratificação por frames pode ocultar desequilíbrio por evento?
- O que prova, tecnicamente, que o holdout ainda está intocado?

## Decisões que devem ser registradas

Registrar coluna/regra temporal, fronteira, política de empates, construção dos grupos, seed, qualidade dos folds e mecanismo de bloqueio do holdout.
