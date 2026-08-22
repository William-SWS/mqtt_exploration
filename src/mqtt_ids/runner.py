"""Runner mínimo com identidade determinística e manifesto autocontido."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable

from mqtt_ids.config import Scenario

SUPPORTED_STAGES = ("diagnostics",)


def run_experiment(
    scenario: Scenario, stages: Iterable[str], output_dir: Path, resume: bool = False
) -> Path:
    """Executa os estágios solicitados e grava sempre o manifesto da execução."""
    selected_stages = tuple(stages)
    unknown_stages = sorted(set(selected_stages).difference(SUPPORTED_STAGES))
    if unknown_stages:
        raise ValueError(f"Estágios desconhecidos: {', '.join(unknown_stages)}")
    if not selected_stages:
        raise ValueError("Selecione pelo menos um estágio.")
    resolved = scenario.as_dict()
    identity = _identity(resolved, selected_stages)
    manifest_path = output_dir / identity / "manifest.json"
    if resume and manifest_path.is_file():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous.get("status") == "completed":
            return manifest_path
    manifest: dict[str, Any] = {
        "identity": identity,
        "config": resolved,
        "stages": list(selected_stages),
        "seed": scenario.seed,
        "started_at": datetime.now(UTC).isoformat(),
        "status": "running",
        "environment": _environment(),
    }
    try:
        for stage in selected_stages:
            if stage == "diagnostics":
                manifest["diagnostics"] = _diagnostics()
        manifest["status"] = "completed"
    except Exception as error:
        manifest["status"] = "failed"
        manifest["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        manifest["finished_at"] = datetime.now(UTC).isoformat()
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return manifest_path


def _identity(config: dict[str, Any], stages: tuple[str, ...]) -> str:
    canonical = json.dumps(
        {"config": config, "stages": stages}, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _environment() -> dict[str, Any]:
    packages: dict[str, str | None] = {}
    for package in ("mqtt-investigation", "PyYAML", "pytest", "ruff", "ipykernel"):
        try:
            packages[package] = version(package)
        except PackageNotFoundError:
            packages[package] = None
    return {
        "platform": platform.platform(),
        "python": sys.version,
        "packages": packages,
    }


def _diagnostics() -> dict[str, Any]:
    return {"runner": "available", "supported_stages": list(SUPPORTED_STAGES)}
