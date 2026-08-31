from pathlib import Path

import pytest

from mqtt_ids import kaggle_assets
from mqtt_ids.kaggle_assets import (
    DatasetMetadata,
    KaggleAssetError,
    acquire_dataset,
    record_published_version,
    sha256,
    upload_model,
)


def test_acquisition_downloads_atomically_and_reuses_valid_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payloads = {
        "Intrusion.csv": b"intrusion",
        "DoS.csv": b"dos",
        "MitM.csv": b"mitm",
    }
    monkeypatch.setattr(
        kaggle_assets,
        "RAW_HASHES",
        {
            name: __import__("hashlib").sha256(value).hexdigest()
            for name, value in payloads.items()
        },
    )
    calls: list[str] = []

    class FakeKaggleHub:
        def dataset_download(self, handle: str, **kwargs: object) -> str:
            calls.append(handle)
            destination = Path(str(kwargs["output_dir"]))
            for category in ("raw", "interim", "processed"):
                (destination / category).mkdir(parents=True)
            for name, value in payloads.items():
                (destination / "raw" / name).write_bytes(value)
            return str(destination)

    monkeypatch.setattr(kaggle_assets, "_kagglehub", lambda: FakeKaggleHub())
    destination = tmp_path / "data"
    metadata = DatasetMetadata(
        doi="10.6084/m9.figshare.24420958",
        license="CC-BY-4.0",
        authors=("Example Author",),
    )

    first = acquire_dataset("owner/data/versions/3", destination, metadata)
    second = acquire_dataset("owner/data/versions/3", destination, metadata)

    assert calls == ["owner/data/versions/3"]
    assert first["reused"] is False
    assert second["reused"] is True
    assert second["owner"] == "owner"
    assert second["slug"] == "data"
    assert second["version"] == 3
    assert second["doi"] == metadata.doi
    assert second["license"] == metadata.license
    assert second["authors"] == ["Example Author"]
    assert {item["name"] for item in second["files"]} == set(payloads)


def test_failed_acquisition_preserves_placeholder_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "data"
    for category in ("raw", "interim", "processed"):
        (destination / category).mkdir(parents=True)
        (destination / category / ".gitkeep").touch()

    class FakeKaggleHub:
        def dataset_download(self, handle: str, **kwargs: object) -> str:
            staged = Path(str(kwargs["output_dir"])) / "raw"
            staged.mkdir(parents=True)
            (staged / "Intrusion.csv").write_bytes(b"corrupted")
            return str(staged.parent)

    monkeypatch.setattr(kaggle_assets, "_kagglehub", lambda: FakeKaggleHub())

    with pytest.raises(KaggleAssetError, match="deve existir exatamente uma vez"):
        acquire_dataset(
            "owner/data/versions/1",
            destination,
            DatasetMetadata("doi", "CC-BY-4.0", ("Author",)),
        )

    assert (destination / "raw" / ".gitkeep").is_file()
    assert not (destination / "raw" / "Intrusion.csv").exists()


def test_versioned_asset_is_recorded_in_local_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"status": "completed"}\n', encoding="utf-8")

    record_published_version(manifest_path, "model", "owner/model/sklearn/baseline/2")

    assert __import__("json").loads(manifest_path.read_text())["published_assets"] == {
        "model": "owner/model/sklearn/baseline/2"
    }


@pytest.mark.parametrize(
    ("validator", "handle"),
    [
        (kaggle_assets.validate_dataset_upload_handle, "owner/data/versions/1"),
        (kaggle_assets.validate_dataset_download_handle, "owner/data"),
        (kaggle_assets.validate_model_upload_handle, "owner/model/sklearn/main/1"),
        (kaggle_assets.validate_model_download_handle, "owner/model/sklearn/main"),
    ],
)
def test_handles_reject_the_wrong_version_form(validator: object, handle: str) -> None:
    with pytest.raises(KaggleAssetError):
        validator(handle)  # type: ignore[operator]


def test_model_upload_validates_package_before_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "model"
    package.mkdir()
    (package / "model.joblib").write_bytes(b"model")
    (package / "metadata.json").write_text("{}\n", encoding="utf-8")
    (package / "manifest.json").write_text("{}\n", encoding="utf-8")
    entries = ["model.joblib", "metadata.json", "manifest.json"]
    (package / "sha256sums.txt").write_text(
        "".join(f"{sha256(package / name)}  {name}\n" for name in entries),
        encoding="utf-8",
    )

    calls: list[tuple[str, str, str]] = []

    class FakeKaggleHub:
        def model_upload(self, handle: str, directory: str, version_notes: str) -> None:
            calls.append((handle, directory, version_notes))

    monkeypatch.setattr(kaggle_assets, "_kagglehub", lambda: FakeKaggleHub())

    upload_model(
        package,
        "owner/mqtt-ids/sklearn/baseline",
        "run abc; dataset owner/data/versions/1",
    )

    assert calls == [
        (
            "owner/mqtt-ids/sklearn/baseline",
            str(package),
            "run abc; dataset owner/data/versions/1",
        )
    ]


def test_model_upload_rejects_a_corrupted_package_before_network(
    tmp_path: Path,
) -> None:
    package = tmp_path / "model"
    package.mkdir()
    (package / "model.joblib").write_bytes(b"model")
    (package / "metadata.json").write_text("{}\n", encoding="utf-8")
    (package / "manifest.json").write_text("{}\n", encoding="utf-8")
    (package / "sha256sums.txt").write_text(
        "0" * 64 + "  model.joblib\n", encoding="utf-8"
    )

    with pytest.raises(KaggleAssetError, match="Hash divergente"):
        upload_model(package, "owner/mqtt-ids/sklearn/baseline", "run abc")
