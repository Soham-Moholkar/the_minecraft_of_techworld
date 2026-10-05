"""Bounded usage tasks shared by the Airflow DAG and native acceptance tests.

URLs and credentials come only from operator environment, never dag_run.conf.
Only numeric aggregates and a digest enter XCom; no datasets or credentials do.
An uncertain consume is retried by the operator: automatic consume retries are
zero because they could advance another batch, despite idempotent sink effects.
"""

import hashlib
import io
import json
import os
import urllib.error
import urllib.request


class PipelineUnavailable(RuntimeError):
    pass


def call(
    suffix: str, payload: dict[str, int] | None = None
) -> tuple[bytes, str | None]:
    if os.environ.get("ATLAS_PIPELINE_ENABLED") != "true":
        raise PipelineUnavailable("usage pipeline disabled")
    token = os.environ.get("ATLAS_PIPELINE_API_TOKEN")
    if not token:
        raise PipelineUnavailable("usage pipeline credential unconfigured")
    base = os.environ.get("ATLAS_PIPELINE_API_URL", "http://api:8000").rstrip("/")

    # The opener disables environment proxies and redirects: credentials must
    # only reach the configured API origin, even when a dependency misbehaves.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    request = urllib.request.Request(
        base + "/v1/streaming/usage" + suffix,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        },
    )
    try:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect()
        )
        with opener.open(request, timeout=15) as response:
            content = response.read(2_000_001)
            if len(content) > 2_000_000:
                raise PipelineUnavailable("usage response too large")
            return content, response.headers.get("X-Atlas-Content-SHA256")
    except Exception:
        raise PipelineUnavailable("usage API unavailable") from None


def consume() -> dict[str, int]:
    raw, _ = call("/consume", {"limit": 100})
    try:
        value = json.loads(raw)
        processed = value["processed"]
        if type(processed) is not int or not 0 <= processed <= 100:
            raise ValueError("batch count")
        return {"processed": processed}
    except Exception:
        raise PipelineUnavailable("invalid consume evidence") from None


def validate_parquet() -> dict[str, int | str]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    raw, digest = call("/export")
    try:
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("digest")
        table = pq.read_table(io.BytesIO(raw))
        if (
            table.schema.names != ["event_id", "units"]
            or table.schema.field("event_id").type != pa.string()
            or table.schema.field("units").type != pa.int64()
            or table.num_rows > 10000
        ):
            raise ValueError("schema or row bound")
        lineage = json.loads((table.schema.metadata or {})[b"atlas.lineage"])
        expected_tenant = os.environ.get("ATLAS_PIPELINE_TENANT", "northstar")
        if lineage["tenant"] != expected_tenant:
            raise ValueError("tenant")
        ids = table.column("event_id").to_pylist()
        units = table.column("units").to_pylist()
        if len(set(ids)) != len(ids) or any(
            type(unit) is not int or not 0 <= unit <= 1000 for unit in units
        ):
            raise ValueError("accepted effects")
        if lineage["rows"] != table.num_rows or lineage["units"] != sum(units):
            raise ValueError("lineage")
        return {"rows": table.num_rows, "units": sum(units), "digest": digest}
    except Exception:
        raise PipelineUnavailable("invalid Parquet lineage") from None


def refresh_lakehouse() -> dict[str, int | bool]:
    raw, _ = call("/lakehouse", {})
    try:
        value = json.loads(raw)
        if (
            value["provider"] != "iceberg-local"
            or type(value["rows"]) is not int
            or not 0 <= value["rows"] <= 10000
            or type(value["changed"]) is not bool
        ):
            raise ValueError("lakehouse response")
        return {"rows": value["rows"], "changed": value["changed"]}
    except Exception:
        raise PipelineUnavailable("invalid lakehouse evidence") from None
