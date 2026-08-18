# Task 12 — Ensemble ponderado

## Objetivo

Medir se modelos calibrados e diversos melhoram o IDS por soft voting, com composição, pesos e limiar escolhidos apenas sobre OOF.

## Pré-requisitos

- Concluir a Task 11 e ler ADR-015.
- Ter probabilidades OOF calibradas e alinhadas de todos os finalistas.
- Entender média ponderada, diversidade de erros e restrições simplex.

## Conceitos e APIs para estudar

- Soft voting e combinação linear de probabilidades.
- Pesos não negativos com soma um; parametrização/normalização estável.
- Optuna para pesos contínuos e limiar, sem retreinar membros no objetivo.
- Enumeração determinística de pares/trios e comparação contra melhores membros.

## Exercício a implementar futuramente

Avaliar o ensemble fixo Decision Tree + Gradient Boosting + melhor MLP. Em paralelo, enumerar todo par e trio contendo a melhor MLP e até dois finalistas tradicionais. Para cada composição, otimizar pesos e limiar apenas nas probabilidades OOF, com orçamento comum. Escolher por Macro-F1, depois recall, log loss e menor número de membros.

## Entregáveis

- Resultado do ensemble fixo e de todas as composições orientadas a dados.
- Pesos, limiar, membros, hashes de predições e estudo de otimização.
- Análise de correlação/complementaridade dos erros.
- Comparação justa com cada membro isolado no mesmo OOF.

## Testes esperados

- Todo peso é finito e ≥ 0; soma é um dentro da tolerância.
- Ensemble de peso unitário reproduz as probabilidades do membro.
- Índices/classes coincidem em todas as matrizes OOF combinadas.
- Enumeração contém somente pares/trios válidos e sempre inclui a MLP.
- Otimização não chama `fit` de nenhum membro e não lê holdout.

## Critérios de aceite

- Ensemble fixo é reportado mesmo que perca para um modelo individual.
- Ensemble orientado a dados segue composição e desempate predefinidos.
- Ganho é comparado com incerteza, custo e complexidade adicionais.
- Configuração final está congelada antes da abertura do teste.

## Perguntas de reflexão

- Probabilidades altamente correlacionadas justificam três membros?
- Otimizar pesos e limiar no mesmo OOF introduz qual otimismo?
- Quando menor número de membros é um desempate operacional importante?

## Decisões que devem ser registradas

Registrar composições enumeradas, parametrização dos pesos, orçamento/seed, ensemble vencedor, diferença para membros e justificativa para adotá-lo ou rejeitá-lo.
