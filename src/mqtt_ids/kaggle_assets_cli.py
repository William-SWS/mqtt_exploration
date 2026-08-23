"""Entrypoint fino para sincronizar ativos Kaggle fora do Git."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from mqtt_ids.kaggle_assets import (
    KaggleAssetError,
    download_dataset,
    download_model,
    upload_dataset,
    upload_model,
)


def main() -> None:
    """Processa comandos explícitos de upload e download Kaggle."""
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Sincroniza ativos privados no Kaggle."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    upload_data = commands.add_parser("upload-dataset")
    upload_data.add_argument(
        "--handle", default=os.getenv("KAGGLE_DATASET_HANDLE")
    )
    upload_data.add_argument("--data-dir", type=Path, default=Path("data"))
    upload_data.add_argument("--version-notes", required=True)

    download_data = commands.add_parser("download-dataset")
    download_data.add_argument(
        "--handle", default=os.getenv("KAGGLE_DATASET_VERSION_HANDLE")
    )
    download_data.add_argument("--data-dir", type=Path, default=Path("data"))
    download_data.add_argument("--category", choices=("raw", "interim", "processed"))

    upload_trained = commands.add_parser("upload-model")
    upload_trained.add_argument("--handle", default=os.getenv("KAGGLE_MODEL_HANDLE"))
    upload_trained.add_argument("--model-dir", required=True, type=Path)
    upload_trained.add_argument("--version-notes", required=True)

    download_trained = commands.add_parser("download-model")
    download_trained.add_argument(
        "--handle", default=os.getenv("KAGGLE_MODEL_VERSION_HANDLE")
    )
    download_trained.add_argument(
        "--output-dir", type=Path, default=Path("artifacts/models")
    )

    arguments = parser.parse_args()
    if not arguments.handle:
        required_variable = {
            "upload-dataset": "KAGGLE_DATASET_HANDLE",
            "download-dataset": "KAGGLE_DATASET_VERSION_HANDLE",
            "upload-model": "KAGGLE_MODEL_HANDLE",
            "download-model": "KAGGLE_MODEL_VERSION_HANDLE",
        }[arguments.command]
        parser.error(f"Informe --handle ou defina {required_variable} no .env.")
    try:
        if arguments.command == "upload-dataset":
            upload_dataset(
                arguments.data_dir, arguments.handle, arguments.version_notes
            )
            print(f"Dataset enviado: {arguments.handle}")
        elif arguments.command == "download-dataset":
            print(
                download_dataset(
                    arguments.handle, arguments.data_dir, arguments.category
                )
            )
        elif arguments.command == "upload-model":
            upload_model(arguments.model_dir, arguments.handle, arguments.version_notes)
            print(f"Modelo enviado: {arguments.handle}")
        else:
            print(download_model(arguments.handle, arguments.output_dir))
    except KaggleAssetError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
