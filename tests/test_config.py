from pathlib import Path

import pytest

from mqtt_ids.config import ScenarioError, load_scenario


def test_scenario_loads_versioned_dataset_provenance(tmp_path: Path) -> None:
    scenario_path = tmp_path / "acquire.yaml"
    scenario_path.write_text(
        """run:
  name: acquire
  seed: 7
dataset:
  handle: owner/data/versions/3
  data_dir: data
  doi: 10.6084/m9.figshare.24420958
  license: CC-BY-4.0
  authors:
    - Example Author
""",
        encoding="utf-8",
    )

    scenario = load_scenario(scenario_path)

    assert scenario.dataset is not None
    assert scenario.dataset.handle == "owner/data/versions/3"
    assert scenario.dataset.authors == ("Example Author",)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("unexpected: true\n", "somente a chave obrigatória"),
        (
            "run:\n name: smoke\n",
            "exatamente 'name' e 'seed'",
        ),
        (
            "run:\n  name: ''\n  seed: 7\n",
            "string não vazia",
        ),
        (
            "run:\n  name: smoke\n  seed: true\n",
            "deve ser um inteiro",
        ),
        ("run: [\n", "YAML inválido"),
    ],
)
def test_invalid_scenarios_raise_clear_error(
    tmp_path: Path, content: str, message: str
) -> None:
    scenario_path = tmp_path / "invalid.yaml"
    scenario_path.write_text(content, encoding="utf-8")

    with pytest.raises(ScenarioError, match=message):
        load_scenario(scenario_path)


def test_missing_scenario_raises_clear_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(ScenarioError, match="Cenário não encontrado"):
        load_scenario(missing_path)
