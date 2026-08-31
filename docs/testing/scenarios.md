# Cenários de teste — runner e ativos Kaggle

Este catálogo descreve os testes atuais da issue 01. O código em `tests/` é a fonte executável; este documento explica a intenção e a forma de executá-los.

## Como executar

```bash
# Testes do runner e CLI
uv run --locked pytest tests/test_runner.py

# Testes da validação de cenário YAML
uv run --locked pytest tests/test_config.py

# Suíte completa
uv run --locked pytest

# Exibir cada cenário executado
uv run --locked pytest -v
```

## Runner e CLI

| Teste | Cenário e entrada | Resultado esperado |
| --- | --- | --- |
| `test_runner_creates_a_deterministic_completed_manifest` | Executa o CLI com YAML válido e depois com `--resume`. | Cria manifesto concluído com seed e diagnóstico; a retomada devolve o mesmo caminho. |
| `test_invalid_scenario_fails_before_creating_output` | Executa o CLI com chave YAML desconhecida. | O processo falha e não cria diretório de saída. |
| `test_same_scenario_has_identity_in_independent_runs` | Executa o mesmo `Scenario(name="smoke", seed=7)` em dois diretórios temporários. | As execuções possuem a mesma identidade. |
| `test_failed_stage_writes_a_failed_manifest` | Simula falha do diagnóstico com `RuntimeError`. | A exceção é propagada e o manifesto registra `status: failed`, tipo, mensagem e seed. |
| `test_cli_records_selected_stage` | Executa o CLI com `--stage diagnostics`. | O manifesto registra o estágio solicitado e `status: completed`. |
| `test_acquisition_failure_is_recorded_in_runner_manifest` | Simula hash divergente no adaptador Kaggle durante `acquire`. | A exceção é propagada e o manifesto registra `status: failed` e mensagem explicativa. |

## Configuração YAML

| Teste | Cenário e entrada | Resultado esperado |
| --- | --- | --- |
| `test_invalid_scenarios_raise_clear_error[unknown-key]` | YAML com uma chave raiz desconhecida. | `ScenarioError` informa que somente `run` é aceito. |
| `test_invalid_scenarios_raise_clear_error[missing-seed]` | `run` contém `name`, mas não `seed`. | `ScenarioError` informa os campos obrigatórios. |
| `test_invalid_scenarios_raise_clear_error[empty-name]` | `run.name` é uma string vazia. | `ScenarioError` informa que o nome não pode ser vazio. |
| `test_invalid_scenarios_raise_clear_error[boolean-seed]` | `run.seed` recebe o booleano YAML `true`. | `ScenarioError` informa que a seed deve ser inteira. |
| `test_invalid_scenarios_raise_clear_error[invalid-yaml]` | YAML possui sintaxe inválida. | `ScenarioError` informa YAML inválido. |
| `test_missing_scenario_raises_clear_error` | O caminho do cenário não existe. | `ScenarioError` informa que o cenário não foi encontrado. |
| `test_scenario_loads_versioned_dataset_provenance` | YAML com handle versionado, destino, DOI, licença e autores. | O contrato de Dataset é carregado com atribuição completa. |

## Ativos Kaggle

Comando mais estreito:

```bash
uv run --locked pytest tests/test_kaggle_assets.py
```

| Teste | Cenário e entrada | Resultado esperado |
| --- | --- | --- |
| `test_acquisition_downloads_atomically_and_reuses_valid_data` | Adaptador Kaggle simulado entrega os três CSVs em `tmp_path`; a aquisição é repetida. | A primeira chamada promove dados validados e grava proveniência; a segunda reutiliza os bytes sem rede. |
| `test_failed_acquisition_preserves_placeholder_destination` | Download incompleto sobre uma árvore que contém apenas `.gitkeep`. | A aquisição falha e preserva integralmente o destino anterior. |
| `test_versioned_asset_is_recorded_in_local_manifest` | Registra uma versão de Model em manifesto temporário. | O handle imutável aparece em `published_assets.model`. |
| `test_handles_reject_the_wrong_version_form` | Handles de Dataset e Model nas formas incompatíveis com upload/download. | Todos falham antes de qualquer chamada remota. |
| `test_model_upload_validates_package_before_network` | Pacote de Model completo com hashes conhecidos e adaptador simulado. | O diretório validado é enviado para a variação esperada. |
| `test_model_upload_rejects_a_corrupted_package_before_network` | Pacote cujo hash declarado diverge. | O upload é recusado antes da rede. |

Os identificadores entre colchetes são nomes descritivos dos casos parametrizados. O pytest pode exibir índices numéricos enquanto os casos não receberem `ids=` explícitos no decorador.
