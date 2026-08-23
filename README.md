# MQTT Intrusion IDS — trilha educacional

Este repositório é uma trilha prática para construir, auditar e comparar um sistema de detecção de intrusão em tráfego MQTT. A prioridade é aprender um processo experimental confiável: proveniência dos dados, prevenção de vazamento, validação temporal, desbalanceamento, seleção de features, calibração, ensembles e reprodutibilidade.

## Como executar

O repositório usa Python 3.12+ e `uv`. Não crie nem ative manualmente um ambiente: `uv run --locked` cria ou sincroniza `.venv` automaticamente a partir de `uv.lock`, sem resolver versões novas. Isso vale tanto para scripts quanto para notebooks.

```bash
uv run --locked mqtt-ids --scenario configs/diagnostics.yaml
uv run --locked mqtt-kaggle-assets --help
uv run --locked pytest
uv run --locked ruff check .
uv run --locked --group notebook jupyter lab
```

O último comando inicia o JupyterLab no mesmo ambiente bloqueado do projeto. Para registrar um kernel de forma explícita, execute `uv run --locked --group notebook python -m ipykernel install --user --name mqtt-investigation`.

O runner aceita `--stage diagnostics`, `--resume` e `--output-dir`. Cada execução válida gera `artifacts/runs/<identidade>/manifest.json`, com cenário resolvido, identidade determinística, seed, versões e status.

## Dados e motivação

A fonte local é o *MQTT Under Attack Dataset*, publicado no Figshare com DOI [`10.6084/m9.figshare.24420958`](https://doi.org/10.6084/m9.figshare.24420958) e licença CC BY 4.0. Os arquivos brutos são `Intrusion.csv`, `DoS.csv` e `MitM.csv`; eles permanecem fora do Git.

Uma inspeção inicial de `Intrusion.csv` encontrou 80.893 frames e 67 colunas (incluindo o alvo `type`), com 1.898 intrusões (2,35%), 30 duplicatas exatas, várias colunas completamente vazias e identificadores de rede fortemente associados à classe. Esses números são hipóteses de contrato a serem confirmadas por testes na implementação, não resultados de modelos.

Hashes SHA-256 observados nesta cópia local:

| Arquivo | SHA-256 |
|---|---|
| `Intrusion.csv` | `730f65a2bd388b973f7088a28b8a37a3a0a56062ad059d90e95da9fffed93518` |
| `DoS.csv` | `e935c819f8bc08898135180029bde0a685e9c5676d5277cacf66d917bb98d4e1` |
| `MitM.csv` | `bfee47413bcf82f3b1433d51db63629a1b61d1a40fc704f545f23c7350daa5d0` |

## Protocolo experimental em uma página

- A política principal será portável: exclui alvo, IP/MAC crus, client IDs, payloads, tópicos crus, timestamps absolutos, número do frame e metadados de captura. Derivações mínimas e generalizáveis poderão ser usadas.
- Duplicatas exatas serão removidas preservando a primeira ocorrência, sem alterar o raw e antes da divisão.
- Os últimos 30% no tempo formarão um holdout intocado. O desenvolvimento usará cinco folds de `StratifiedGroupKFold`, com grupos temporais primários de 30 s e sensibilidades de 10 s e 60 s para finalistas.
- Pré-processamento, SMOTENC e seleção supervisionada serão ajustados somente dentro de cada fold.
- O screening terá exatamente 192 registros: 8 modelos × 8 caminhos de features × 3 regimes. Combinações inviáveis continuarão na tabela com status `failed` e motivo.
- Macro-F1 é o objetivo principal. Desempates: recall de intrusão, log loss, latência em nuvem e tamanho do artefato.
- O teste temporal será aberto apenas depois de congelar features, regime, hiperparâmetros, calibração e limiar.
- Resultados serão avaliados por frame e por evento; intervalos de 95% usarão bootstrap de 2.000 reamostragens por blocos temporais.

## Roteiro

| Etapa | Tema | Documento |
|---:|---|---|
| 00 | Fundamentos do projeto | [`00_project_foundations.md`](docs/tasks/00_project_foundations.md) |
| 01 | Kaggle e proveniência | [`01_kaggle_dataset.md`](docs/tasks/01_kaggle_dataset.md) |
| 02 | EDA e auditoria | [`02_eda_and_data_audit.md`](docs/tasks/02_eda_and_data_audit.md) |
| 03 | Contrato e limpeza | [`03_data_contract_and_cleaning.md`](docs/tasks/03_data_contract_and_cleaning.md) |
| 04 | Divisão e validação | [`04_splitting_and_validation.md`](docs/tasks/04_splitting_and_validation.md) |
| 05 | Pré-processamento e desbalanceamento | [`05_preprocessing_and_imbalance.md`](docs/tasks/05_preprocessing_and_imbalance.md) |
| 06 | Baselines tradicionais | [`06_traditional_baselines.md`](docs/tasks/06_traditional_baselines.md) |
| 07 | Seleção de features | [`07_feature_selection.md`](docs/tasks/07_feature_selection.md) |
| 08 | Screening experimental | [`08_experiment_screening.md`](docs/tasks/08_experiment_screening.md) |
| 09 | Otimização com Optuna | [`09_optuna_optimization.md`](docs/tasks/09_optuna_optimization.md) |
| 10 | Tiny MLP | [`10_tiny_mlp.md`](docs/tasks/10_tiny_mlp.md) |
| 11 | Calibração e limiares | [`11_calibration_and_thresholds.md`](docs/tasks/11_calibration_and_thresholds.md) |
| 12 | Ensemble ponderado | [`12_weighted_ensemble.md`](docs/tasks/12_weighted_ensemble.md) |
| 13 | Relato e reprodutibilidade | [`13_reporting_and_reproducibility.md`](docs/tasks/13_reporting_and_reproducibility.md) |
| 14 | Benchmark edge futuro | [`14_future_edge_benchmark.md`](docs/tasks/14_future_edge_benchmark.md) |

As decisões de desenho e suas consequências estão em [`docs/DECISIONS.md`](docs/DECISIONS.md). O arquivo é append-only: decisões novas ganham novas entradas; as antigas não são reescritas silenciosamente.

## Estrutura

```text
docs/                 documentação e tarefas guiadas
notebooks/            exploração futura, sem lógica de produção
src/mqtt_ids/         biblioteca Python futura
scripts/              entrypoints pequenos no futuro
configs/              cenários YAML futuros
data/                 raw, interim e processed; conteúdo ignorado
artifacts/            manifests, modelos e estudos; conteúdo ignorado
results/               tabelas e figuras; conteúdo ignorado
tests/                 testes futuros
```

## Princípios de trabalho

Documentação e comunicação ficam em PT-BR; nomes de módulos, APIs e código futuro ficam em inglês. Scripts chamarão funções da biblioteca, nunca outros scripts por `subprocess`. Dados brutos são imutáveis, credenciais nunca entram no repositório e alegações sobre Raspberry Pi só poderão aparecer depois de medições reais.
