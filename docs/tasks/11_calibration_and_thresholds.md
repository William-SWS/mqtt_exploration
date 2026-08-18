# Task 11 — Calibração e limiares

## Objetivo

Transformar scores dos finalistas em probabilidades avaliáveis e escolher um limiar operacional exclusivamente a partir de previsões de desenvolvimento.

## Pré-requisitos

- Concluir a Task 10 e ler ADR-014.
- Congelar finalistas tradicionais e MLP antes da calibração.
- Entender discriminação, calibração e decisão como problemas distintos.

## Conceitos e APIs para estudar

- `CalibratedClassifierCV`, métodos `sigmoid` e `isotonic` e CV de calibração.
- `log_loss`, Brier score opcional, `calibration_curve`/`CalibrationDisplay`.
- Busca de limiar sobre probabilidades OOF e viés de reutilizar as mesmas previsões.
- Métricas em limiar 0,5 versus limiar ajustado; restrições de recall/FPR.

## Exercício a implementar futuramente

Para cada finalista, gerar probabilidades OOF sem permitir que a amostra usada para calibrar também avalie o calibrador. Comparar sigmoid e isotonic com protocolo aninhado/particionado apropriado, escolher pela regra congelada e ajustar um limiar para Macro-F1 com desempates globais. Preservar resultados de 0,5. Preparar o fit final sem abrir o holdout.

## Entregáveis

- Artefato de calibração e curva/reliability table por finalista.
- Tabela OOF com probabilidades brutas/calibradas e decisões nos dois limiares.
- Limiar escolhido, função objetivo e regra de desempate.
- Relatório de log loss, calibração e mudanças em recall/FPR.

## Testes esperados

- Probabilidades são finitas, limitadas e alinhadas aos índices.
- Cada calibrador vê apenas predições/labels permitidos pelo seu split.
- Recalcular o limiar sobre o mesmo OOF produz o mesmo valor.
- Limiar 0,5 permanece reportado e não é sobrescrito pelo ajustado.
- Holdout não participa de calibração, escolha de método ou limiar.

## Critérios de aceite

- Calibração é aplicada somente aos finalistas.
- Escolha entre sigmoid/isotonic considera generalização, não ajuste aparente.
- Métricas antes/depois são reportadas, inclusive quando a calibração piora Macro-F1.
- Configuração congelada contém calibrador e limiar por modelo.

## Perguntas de reflexão

- Um classificador pode ter ótimo ranking e probabilidades ruins?
- Por que isotonic tende a exigir mais dados que sigmoid?
- Qual custo operacional não aparece ao maximizar apenas Macro-F1?

## Decisões que devem ser registradas

Registrar protocolo de calibração, método por finalista, grid/regra do limiar, métricas usadas e qualquer restrição operacional adicional.
