"""Carregamento seguro e validação do cenário de execução."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ScenarioError(ValueError):
    """Indica um cenário ausente ou incompatível com o contrato mínimo."""


@dataclass(frozen=True)
class Scenario:
    """Configuração já validada do runner."""

    name: str
    seed: int

    def as_dict(self) -> dict[str, Any]:
        return {"run": {"name": self.name, "seed": self.seed}}


def load_scenario(path: Path) -> Scenario:
    """Lê um YAML seguro e falha antes de qualquer estágio ser executado."""
    if not path.is_file():
        raise ScenarioError(f"Cenário não encontrado: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ScenarioError(f"YAML inválido em {path}: {error}") from error
    if not isinstance(raw, dict):
        raise ScenarioError("O cenário deve ser um mapa YAML.")
    if set(raw) != {"run"}:
        raise ScenarioError("O cenário aceita somente a chave obrigatória 'run'.")
    run = raw["run"]
    if not isinstance(run, dict) or set(run) != {"name", "seed"}:
        raise ScenarioError("'run' deve conter exatamente 'name' e 'seed'.")
    name, seed = run["name"], run["seed"]
    if not isinstance(name, str) or not name.strip():
        raise ScenarioError("'run.name' deve ser uma string não vazia.")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ScenarioError("'run.seed' deve ser um inteiro.")
    return Scenario(name=name.strip(), seed=seed)
