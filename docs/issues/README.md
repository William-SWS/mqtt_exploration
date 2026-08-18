# Issue drafts — MQTT Intrusion IDS

Estes documentos são os corpos aprovados das issues derivadas do PRD. Cada issue é um tracer bullet verificável, contém tópicos de estudo, ferramentas recomendadas, critérios de aceite, dependências e histórias cobertas.

## Ordem de publicação

| Ordem | Issue | Dependências |
|---:|---|---|
| 01 | Projeto reproduzível e runner mínimo | nenhuma |
| 02 | Dataset Kaggle versionado | 01 |
| 03 | Auditoria e dicionário de dados | 02 |
| 04 | Contrato, limpeza e features portáveis | 02, 03 |
| 05 | Holdout temporal e folds agrupados | 04 |
| 06 | Baseline OOF end-to-end | 05 |
| 07 | Regimes de desbalanceamento | 06 |
| 08 | Oito modelos tradicionais | 06, 07 |
| 09 | Oito caminhos de features | 06, 07 |
| 10 | Screening de 192 configurações | 08, 09 |
| 11 | Otimização Optuna | 10 |
| 12 | Tiny MLP não inferior | 11 |
| 13 | Calibração e limiares | 11, 12 |
| 14 | Ensembles ponderados | 13 |
| 15 | Holdout e relatório final | 14 |
| 16 | Especificação edge futura | 15 |

## Publicação

Na publicação em GitHub Issues, substituir cada placeholder `{{ISSUE_NN}}` pelo identificador real criado anteriormente e aplicar somente o label de triagem `ready-for-agent`. O PRD é a fonte local; ele não deve ser fechado ou modificado pela publicação destas issues.
