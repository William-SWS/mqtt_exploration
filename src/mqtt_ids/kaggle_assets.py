"""Sincronização verificável de ativos privados versionados no Kaggle."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

RAW_HASHES = {
    "Intrusion.csv": "730f65a2bd388b973f7088a28b8a37a3a0a56062ad059d90e95da9fffed93518",
    "DoS.csv": "e935c819f8bc08898135180029bde0a685e9c5676d5277cacf66d917bb98d4e1",
    "MitM.csv": "bfee47413bcf82f3b1433d51db63629a1b61d1a40fc704f545f23c7350daa5d0",
}

_DATASET_UPLOAD = re.compile(r"^[^/]+/[^/]+$")
_DATASET_DOWNLOAD = re.compile(r"^[^/]+/[^/]+/versions/[1-9][0-9]*$")
_MODEL_UPLOAD = re.compile(r"^[^/]+/[^/]+/[^/]+/[^/]+$")
_MODEL_DOWNLOAD = re.compile(r"^[^/]+/[^/]+/[^/]+/[^/]+/[1-9][0-9]*$")
_CATEGORIES = frozenset({"raw", "interim", "processed"})


class KaggleAssetError(ValueError):
    """Indica que um ativo não atende ao contrato antes da chamada remota."""


def sha256(path: Path) -> str:
    """Calcula SHA-256 em streaming, sem carregar o arquivo integralmente."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_dataset_upload_handle(handle: str) -> None:
    """Exige handle sem versão para criar ou publicar uma nova versão."""
    if not _DATASET_UPLOAD.fullmatch(handle):
        raise KaggleAssetError(
            "Handle de upload de Dataset deve ser 'owner/slug', sem versão."
        )


def validate_dataset_download_handle(handle: str) -> None:
    """Exige versão explícita para restaurar dados reproduzíveis."""
    if not _DATASET_DOWNLOAD.fullmatch(handle):
        raise KaggleAssetError(
            "Handle de download de Dataset deve ser 'owner/slug/versions/N'."
        )


def validate_model_upload_handle(handle: str) -> None:
    """Exige handle de variação sem versão para publicar um modelo."""
    if not _MODEL_UPLOAD.fullmatch(handle):
        raise KaggleAssetError(
            "Handle de upload de Model deve ser 'owner/model/framework/variation'."
        )


def validate_model_download_handle(handle: str) -> None:
    """Exige versão explícita para restaurar um modelo reproduzível."""
    if not _MODEL_DOWNLOAD.fullmatch(handle):
        raise KaggleAssetError(
            "Handle de download de Model deve ser "
            "'owner/model/framework/variation/N'."
        )


def prepare_dataset_package(data_dir: Path, package_dir: Path) -> Path:
    """Copia ``data`` e escreve um manifesto de hashes para o upload atômico."""
    _validate_categories(data_dir)
    raw_files = _find_raw_files(data_dir / "raw")
    for name, expected_hash in RAW_HASHES.items():
        observed_hash = sha256(raw_files[name])
        if observed_hash != expected_hash:
            raise KaggleAssetError(
                f"SHA-256 divergente para {name}: esperado {expected_hash}, "
                f"observado {observed_hash}."
            )
    if package_dir.exists():
        raise KaggleAssetError(f"Diretório de pacote já existe: {package_dir}")
    shutil.copytree(data_dir, package_dir, ignore=shutil.ignore_patterns(".gitkeep"))
    manifest = {
        "categories": sorted(_CATEGORIES),
        "raw_files": [
            {
                "name": name,
                "path": str(raw_files[name].relative_to(data_dir)),
                "size_bytes": raw_files[name].stat().st_size,
                "sha256": sha256(raw_files[name]),
            }
            for name in sorted(RAW_HASHES)
        ],
    }
    (package_dir / "kaggle-provenance.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return package_dir


def upload_dataset(data_dir: Path, handle: str, version_notes: str) -> None:
    """Publica uma nova versão privada de toda a árvore de dados."""
    validate_dataset_upload_handle(handle)
    if not version_notes.strip():
        raise KaggleAssetError("A versão do Dataset exige uma nota não vazia.")
    with tempfile.TemporaryDirectory(prefix="mqtt-kaggle-dataset-") as temporary:
        package_dir = prepare_dataset_package(data_dir, Path(temporary) / "data")
        _kagglehub().dataset_upload(
            handle, str(package_dir), version_notes=version_notes.strip()
        )


def download_dataset(
    handle: str, data_dir: Path, category: str | None = None
) -> Path:
    """Restaura todo o Dataset ou uma categoria em ``data_dir`` e valida raw."""
    validate_dataset_download_handle(handle)
    if category is not None and category not in _CATEGORIES:
        raise KaggleAssetError("Categoria deve ser raw, interim ou processed.")
    result = _kagglehub().dataset_download(
        handle, path=category, output_dir=str(data_dir)
    )
    if category in (None, "raw"):
        _validate_downloaded_raw(data_dir / "raw")
    return Path(result)


def validate_model_package(model_dir: Path) -> None:
    """Garante que o modelo inclua pesos, metadata, manifesto e hashes."""
    required = ("metadata.json", "manifest.json", "sha256sums.txt")
    missing = [name for name in required if not (model_dir / name).is_file()]
    model_files = (
        [
            path
            for path in model_dir.iterdir()
            if path.is_file() and path.suffix in {".joblib", ".pt", ".pth"}
        ]
        if model_dir.is_dir()
        else []
    )
    if missing or not model_files:
        details = []
        if missing:
            details.append("faltam " + ", ".join(missing))
        if not model_files:
            details.append("falta um .joblib, .pt ou .pth")
        raise KaggleAssetError("Pacote de modelo inválido: " + "; ".join(details) + ".")
    expected = _parse_sha256sums(model_dir / "sha256sums.txt")
    for relative_path, expected_hash in expected.items():
        path = model_dir / relative_path
        if not path.is_file() or sha256(path) != expected_hash:
            raise KaggleAssetError(
                f"Hash divergente ou arquivo ausente: {relative_path}."
            )


def upload_model(model_dir: Path, handle: str, version_notes: str) -> None:
    """Publica o pacote de um modelo em sua variação privada no Kaggle."""
    validate_model_upload_handle(handle)
    if not version_notes.strip():
        raise KaggleAssetError("A versão do Model exige uma nota não vazia.")
    validate_model_package(model_dir)
    _kagglehub().model_upload(
        handle, str(model_dir), version_notes=version_notes.strip()
    )


def download_model(handle: str, output_dir: Path) -> Path:
    """Restaura e valida um pacote de modelo com versão explícita."""
    validate_model_download_handle(handle)
    result = Path(_kagglehub().model_download(handle, output_dir=str(output_dir)))
    validate_model_package(result)
    return result


def _validate_categories(data_dir: Path) -> None:
    missing = [name for name in sorted(_CATEGORIES) if not (data_dir / name).is_dir()]
    if missing:
        raise KaggleAssetError("Diretórios de dados ausentes: " + ", ".join(missing))


def _find_raw_files(raw_dir: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for name in RAW_HASHES:
        matches = list(raw_dir.rglob(name)) if raw_dir.is_dir() else []
        if len(matches) != 1:
            raise KaggleAssetError(
                f"{name} deve existir exatamente uma vez dentro de {raw_dir}."
            )
        found[name] = matches[0]
    return found


def _validate_downloaded_raw(raw_dir: Path) -> None:
    raw_files = _find_raw_files(raw_dir)
    for name, expected_hash in RAW_HASHES.items():
        path = raw_files[name]
        if sha256(path) != expected_hash:
            raise KaggleAssetError(f"SHA-256 divergente após download: {path}.")


def _parse_sha256sums(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, separator, relative_path = line.partition("  ")
        if not separator or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise KaggleAssetError(f"Linha inválida em {path}: {line!r}.")
        entries[relative_path] = digest
    if not entries:
        raise KaggleAssetError(f"{path} não pode estar vazio.")
    return entries


def _kagglehub() -> Any:
    try:
        import kagglehub
    except ImportError as error:  # pragma: no cover - protegido por dependência.
        raise KaggleAssetError("Instale a dependência kagglehub.") from error
    return kagglehub
