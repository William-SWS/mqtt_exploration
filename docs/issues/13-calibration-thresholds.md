# Calibrar probabilidades e ajustar limiares OOF

## What to build

Adicionar um estágio para calibrar somente os finalistas tradicionais e a MLP, comparar sigmoid e isotonic com separação adequada entre ajuste e avaliação e escolher um limiar usando apenas probabilidades OOF. Preservar e reportar em paralelo as decisões com limiar 0,5 e com limiar ajustado.

## What to study

- Diferenças entre discriminação, calibração e decisão.
- Platt/sigmoid versus isotonic; sobreajuste com poucos exemplos de calibração.
- CalibratedClassifierCV, estimador congelado e necessidade de amostras disjuntas.
- Busca de limiar, log loss, reliability diagrams e eventual Brier score diagnóstico.

## Recommended tools and libraries

- scikit-learn para CalibratedClassifierCV, calibration curve/display e métricas.
- NumPy/pandas para busca determinística e armazenamento das probabilidades OOF.
- Matplotlib/Seaborn para reliability diagrams consistentes.
- pytest para separação de amostras, bounds, alinhamento e determinismo do limiar.

## Acceptance criteria

- [ ] Apenas finalistas congelados entram na calibração.
- [ ] Nenhuma amostra avalia um calibrador ou base estimator que a usou no fit indevido.
- [ ] Sigmoid e isotonic são comparados pela regra documentada, inclusive quando ambos pioram resultados.
- [ ] Probabilidades brutas/calibradas são finitas, limitadas e alinhadas.
- [ ] Limiar 0,5 e limiar ajustado permanecem disponíveis e identificados separadamente.
- [ ] Configuração congelável registra método, parâmetros, limiar e métricas OOF.
- [ ] O holdout não participa de nenhuma escolha.

## Blocked by

- {{ISSUE_11}}
- {{ISSUE_12}}

## User stories covered

79–83.
