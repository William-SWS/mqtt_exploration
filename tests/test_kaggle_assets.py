from pathlib import Path

import pytest

from mqtt_ids import kaggle_assets
from mqtt_ids.kaggle_assets import KaggleAssetError, sha256, upload_model


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
