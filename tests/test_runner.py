import json
import subprocess
import sys
from pathlib import Path

import pytest

from mqtt_ids import runner
from mqtt_ids.config import Scenario
from mqtt_ids.runner import run_experiment


def test_runner_creates_a_deterministic_completed_manifest(tmp_path: Path) -> None:
    scenario = tmp_path / "scenario.yaml"
    scenario.write_text("run:\n  name: smoke\n  seed: 7\n", encoding="utf-8")
    output_dir = tmp_path / "runs"
    command = [
        sys.executable,
        "-m",
        "mqtt_ids.cli",
        "--scenario",
        str(scenario),
        "--output-dir",
        str(output_dir),
    ]
    first = subprocess.run(command, check=True, capture_output=True, text=True)
    manifest_path = Path(first.stdout.strip())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    second = subprocess.run(
        [*command, "--resume"], check=True, capture_output=True, text=True
    )
    assert manifest["status"] == "completed"
    assert manifest["seed"] == 7
    assert manifest["diagnostics"]["runner"] == "available"
    assert second.stdout.strip() == str(manifest_path)


def test_invalid_scenario_fails_before_creating_output(tmp_path: Path) -> None:
    scenario = tmp_path / "invalid.yaml"
    scenario.write_text("unexpected: true\n", encoding="utf-8")
    output_dir = tmp_path / "runs"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mqtt_ids.cli",
            "--scenario",
            str(scenario),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert not output_dir.exists()


def test_same_scenario_has_identity_in_independent_runs(
    tmp_path: Path,
) -> None:
    scenario = Scenario(name="smoke", seed=7)

    first_manifest = run_experiment(
        scenario=scenario,
        stages=["diagnostics"],
        output_dir=tmp_path / "first",
    )
    second_manifest = run_experiment(
        scenario=scenario,
        stages=["diagnostics"],
        output_dir=tmp_path / "second",
    )

    assert first_manifest.parent.name == second_manifest.parent.name


def test_failed_stage_writes_a_failed_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_diagnostics() -> dict[str, str]:
        raise RuntimeError("diagnóstico interrompido")

    monkeypatch.setattr(runner, "_diagnostics", fail_diagnostics)
    output_dir = tmp_path / "runs"

    with pytest.raises(RuntimeError, match="diagnóstico interrompido"):
        runner.run_experiment(
            scenario=Scenario(name="failure-test", seed=7),
            stages=["diagnostics"],
            output_dir=output_dir,
        )

    manifest_path = next(output_dir.glob("*/manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["status"] == "failed"
    assert manifest["error"] == {
        "type": "RuntimeError",
        "message": "diagnóstico interrompido",
    }
    assert manifest["seed"] == 7


def test_cli_records_selected_stage(tmp_path: Path) -> None:
    scenario = tmp_path / "scenario.yaml"
    scenario.write_text("run:\n  name: smoke\n  seed: 7\n", encoding="utf-8")
    output_dir = tmp_path / "runs"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mqtt_ids.cli",
            "--scenario",
            str(scenario),
            "--stage",
            "diagnostics",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    manifest_path = Path(result.stdout.strip())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["stages"] == ["diagnostics"]
    assert manifest["status"] == "completed"
