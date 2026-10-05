"""Publish one tenant's accepted usage aggregate to a BI-only SQLite database.

Superset never receives the application's database or raw event identifiers.
This operator job uses the authenticated, bounded export and writes only the
numeric aggregate/digest. A read-only mount and SQLite URI protect the projection.
"""

import importlib.util
import os
import re
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def owned_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("owned usage module unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def publish(raw: bytes, digest: str, tenant: str, root: Path) -> Path:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", tenant):
        raise ValueError("tenant")
    validator = owned_module("atlas_bi_source", ROOT / "infra/spark/usage_job.py")
    provider, rows, units = validator.validate_source(raw, digest, tenant)
    root = root.resolve()
    folder = root / tenant / provider
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "usage.db"
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise ValueError("BI output containment")
    with closing(sqlite3.connect(path, timeout=3)) as db, db:
        # One row, one namespace, one transaction. A reader sees the old or new
        # projection; no journal/WAL is copied from the application database.
        db.execute(
            "CREATE TABLE IF NOT EXISTS usage_rollup (tenant TEXT PRIMARY KEY, source_provider TEXT, rows INTEGER CHECK(rows BETWEEN 0 AND 10000), units INTEGER CHECK(units BETWEEN 0 AND rows*1000), source_digest TEXT, refreshed_at TEXT)"
        )
        db.execute("DELETE FROM usage_rollup")
        db.execute(
            "INSERT INTO usage_rollup VALUES (?,?,?,?,?,?)",
            (tenant, provider, rows, units, digest, datetime.now(UTC).isoformat()),
        )
    return path


def main() -> None:
    transport = owned_module(
        "atlas_bi_transport", ROOT / "infra/airflow/dags/atlas_usage_tasks.py"
    )
    raw, digest = transport.call("/export")
    if digest is None:
        raise ValueError("source digest unavailable")
    path = publish(
        raw,
        digest,
        os.environ.get("ATLAS_PIPELINE_TENANT", "northstar"),
        Path(os.environ.get("ATLAS_USAGE_BI_STORE", "artifacts/usage-bi")),
    )
    # Numeric operational evidence only; no credential, raw row or local path.
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        row = db.execute("SELECT rows,units FROM usage_rollup").fetchone()
    print(f"usage_bi_projection rows={row[0]} units={row[1]}")


if __name__ == "__main__":
    main()
