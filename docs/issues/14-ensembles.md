# Construir e selecionar ensembles ponderados

## What to build

Adicionar um estágio de soft voting que avalie o ensemble fixo DT+GB+MLP e enumere pares/trios contendo a melhor MLP e até dois finalistas tradicionais. Otimizar pesos não negativos normalizados e limiar sobre OOF, comparar cada combinação com seus membros e congelar o vencedor pela regra de desempate.

## What to study

- Soft voting, diversidade de erro, correlação entre probabilidades e calibração.
- Otimização sobre simplex e parametrizações que garantem pesos válidos.
- Risco de otimizar pesos e limiar na mesma amostra OOF.
- Complexidade operacional versus ganho estatístico.

## Recommended tools and libraries

- NumPy para combinação vetorizada e validação de simplex.
- Optuna para pesos/limiar com orçamento comum entre composições.
- pandas para enumeração, ranking e análise de erros.
- pytest parametrizado para combinações, alinhamento, soma dos pesos e peso unitário.

## Acceptance criteria

- [ ] O ensemble fixo é sempre avaliado e reportado, mesmo que não vença.
- [ ] Toda composição orientada a dados tem dois ou três membros e inclui a melhor MLP.
- [ ] Pesos são finitos, não negativos e somam um dentro da tolerância.
- [ ] Peso unitário reproduz exatamente a probabilidade do membro correspondente.
- [ ] Otimização consome somente matrizes OOF alinhadas e nunca chama `fit` dos membros.
- [ ] Ranking segue Macro-F1, recall, log loss e menor número de membros conforme política.
- [ ] Composição, pesos e limiar vencedores são congelados antes do holdout.

## Blocked by

- {{ISSUE_13}}

## User stories covered

84–89.
