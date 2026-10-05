"""Canonical local URIs and remote filesystem denial at the FileIO boundary."""

import os
from pathlib import Path

import pytest


def test_local_uri_spaces_and_windows_drive() -> None:
    pytest.importorskip("pyiceberg")
    from atlas_api.local_iceberg_io import LocalIcebergFileIO

    path = Path("output") / "lake with spaces%20" / "metadata"
    scheme, _, native = LocalIcebergFileIO.parse_location(path.resolve().as_uri())
    assert scheme == "file"
    assert "lake with spaces%20" in native
    if os.name == "nt":
        assert native.startswith("//?/")
        assert not native.startswith("//?//C:")


def test_remote_io_is_denied() -> None:
    pytest.importorskip("pyiceberg")
    from atlas_api.local_iceberg_io import LocalIcebergFileIO

    with pytest.raises(ValueError, match="remote"):
        LocalIcebergFileIO.parse_location("s3://private-bucket/data.parquet")
    with pytest.raises(ValueError, match="remote"):
        LocalIcebergFileIO.parse_location("file://remote-server/share/data.parquet")
