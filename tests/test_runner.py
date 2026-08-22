import json
import subprocess
import sys
from pathlib import Path


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
