"""Carregamento seguro e validação do cenário de execução."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ScenarioError(ValueError):
    """Indica um cenário ausente ou incompatível com o contrato mínimo."""


@dataclass(frozen=True)
class DatasetConfig:
    """Fonte Kaggle versionada e sua atribuição verificável."""

    handle: str
    data_dir: Path
    doi: str
    license: str
    authors: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "handle": self.handle,
            "data_dir": str(self.data_dir),
            "doi": self.doi,
            "license": self.license,
            "authors": list(self.authors),
        }


@dataclass(frozen=True)
class Scenario:
    """Configuração já validada do runner."""

    name: str
    seed: int
    dataset: DatasetConfig | None = None

    def as_dict(self) -> dict[str, Any]:
        resolved: dict[str, Any] = {"run": {"name": self.name, "seed": self.seed}}
        if self.dataset is not None:
            resolved["dataset"] = self.dataset.as_dict()
        return resolved


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
    if "run" not in raw or not set(raw).issubset({"run", "dataset"}):
        raise ScenarioError(
            "O cenário aceita somente a chave obrigatória 'run' e a opcional 'dataset'."
        )
    run = raw["run"]
    if not isinstance(run, dict) or set(run) != {"name", "seed"}:
        raise ScenarioError("'run' deve conter exatamente 'name' e 'seed'.")
    name, seed = run["name"], run["seed"]
    if not isinstance(name, str) or not name.strip():
        raise ScenarioError("'run.name' deve ser uma string não vazia.")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ScenarioError("'run.seed' deve ser um inteiro.")
    return Scenario(
        name=name.strip(), seed=seed, dataset=_load_dataset(raw.get("dataset"))
    )


def _load_dataset(raw: object) -> DatasetConfig | None:
    if raw is None:
        return None
    fields = {"handle", "data_dir", "doi", "license", "authors"}
    if not isinstance(raw, dict) or set(raw) != fields:
        raise ScenarioError(
            "'dataset' deve conter exatamente handle, data_dir, doi, license e authors."
        )
    strings = {name: raw[name] for name in fields - {"authors"}}
    if any(
        not isinstance(value, str) or not value.strip() for value in strings.values()
    ):
        raise ScenarioError("Os campos textuais de 'dataset' devem ser não vazios.")
    authors = raw["authors"]
    if (
        not isinstance(authors, list)
        or not authors
        or any(not isinstance(author, str) or not author.strip() for author in authors)
    ):
        raise ScenarioError("'dataset.authors' deve ser uma lista não vazia.")
    return DatasetConfig(
        handle=strings["handle"].strip(),
        data_dir=Path(strings["data_dir"].strip()),
        doi=strings["doi"].strip(),
        license=strings["license"].strip(),
        authors=tuple(author.strip() for author in authors),
    )
