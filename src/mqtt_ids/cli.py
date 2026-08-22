"""Interface de linha de comando do runner."""

from __future__ import annotations

import argparse
from pathlib import Path

from mqtt_ids.config import ScenarioError, load_scenario
from mqtt_ids.runner import SUPPORTED_STAGES, run_experiment


def main() -> None:
    """Processa argumentos e imprime o caminho do manifesto produzido."""
    parser = argparse.ArgumentParser(description="Executa um cenário MQTT IDS.")
    parser.add_argument("--scenario", required=True, type=Path)
    parser.add_argument("--stage", action="append", choices=SUPPORTED_STAGES)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/runs"))
    arguments = parser.parse_args()
    try:
        scenario = load_scenario(arguments.scenario)
        manifest = run_experiment(
            scenario,
            arguments.stage or ["diagnostics"],
            arguments.output_dir,
            arguments.resume,
        )
    except (ScenarioError, ValueError) as error:
        parser.error(str(error))
    print(manifest)


if __name__ == "__main__":
    main()
