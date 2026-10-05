"""Bounded operational dataset profiling with interchangeable aggregation engines.

CSV is data, never executable SQL or a filename. Foundation cleaning is explicit;
pandas materializes the typed frame, NumPy profiles its distribution, SciPy
estimates uncertainty, and Polars/DuckDB independently check the grouped result.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
import re
import time
from datetime import UTC, datetime
from importlib.metadata import version
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

MAX_ROWS = 5000
MAX_BYTES = 262144
Row = dict[str, str | float | int]


class DatasetImport(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=120)
    csv_text: str = Field(min_length=1, max_length=MAX_BYTES)


class ServiceAggregate(BaseModel):
    service: str
    cost: float
    requests: int


class HistogramBucket(BaseModel):
    lower: float
    upper: float
    count: int


class EngineEvidence(BaseModel):
    engine: Literal["pandas", "polars", "duckdb"]
    version: str
    p50_ms: float
    p95_ms: float
    repetitions: int
    matches_reference: bool


class DatasetProfile(BaseModel):
    input_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    service_count: int
    cost_total: float
    cost_mean: float
    cost_median: float
    cost_p95: float
    cost_stddev: float
    mean_ci95: list[float] | None
    histogram: list[HistogramBucket]
    services: list[ServiceAggregate]
    engines: list[EngineEvidence]
    caveats: list[str]
    generated_at: datetime


class DatasetSummary(BaseModel):
    id: UUID
    name: str
    source_checksum: str
    created_at: datetime
    valid_rows: int


class DatasetRead(DatasetSummary):
    profile: DatasetProfile


def generate_sample(row_count: int = 1000) -> str:
    """Deterministic synthetic operational fixture with known quality defects."""
    if not 3 <= row_count <= MAX_ROWS:
        raise ValueError("sample size must be between 3 and 5000")
    lines = ["date,service,cost,requests"]
    for index in range(row_count - 2):
        lines.append(
            f"2026-09-{1 + index % 28:02d},{('api', 'worker', 'search')[index % 3]},"
            f"{4 + index * 1.7:.2f},{100 + index * 23}"
        )
    lines.extend([lines[1], "2026-09-02,worker,invalid,20"])
    return "\n".join(lines) + "\n"


def clean_csv(text: str) -> tuple[list[Row], int, int, int]:
    """Normalize each record, reject invalid measurements, and deduplicate rows.

    Invalid rows are counted rather than silently imputing operational costs.
    No formula evaluation, file access, URL fetching, or caller-defined schema is
    involved. Limits bound memory, group cardinality, and interactive CPU work.
    """
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("CSV exceeds the 256 KiB import limit")
    reader = csv.DictReader(io.StringIO(text), strict=True)
    try:
        fieldnames = reader.fieldnames
    except csv.Error as error:
        raise ValueError("malformed CSV header") from error
    if fieldnames != ["date", "service", "cost", "requests"]:
        raise ValueError("CSV header must be date,service,cost,requests")
    clean: list[Row] = []
    seen: set[tuple[str, str, float, int]] = set()
    total = invalid = duplicate = 0
    try:
        for row in reader:
            total += 1
            if total > MAX_ROWS:
                raise ValueError("CSV exceeds the 5000-row interactive limit")
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("wrong number of columns")
                date = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date().isoformat()
                service = row["service"].strip().lower()
                if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", service):
                    raise ValueError("invalid service")
                cost = float(row["cost"].strip())
                requests = int(row["requests"].strip())
                if (
                    not math.isfinite(cost)
                    or not 0 <= cost <= 1_000_000
                    or not 0 <= requests <= 10**9
                ):
                    raise ValueError("measurement out of range")
                identity = (date, service, cost, requests)
                if identity in seen:
                    duplicate += 1
                    continue
                seen.add(identity)
                clean.append({"date": date, "service": service, "cost": cost, "requests": requests})
            except (ValueError, TypeError, AttributeError):
                invalid += 1
    except csv.Error as error:
        raise ValueError("malformed CSV") from error
    if not clean:
        raise ValueError("CSV contains no valid operational measurements")
    if len({row["service"] for row in clean}) > 100:
        raise ValueError("CSV exceeds the 100-service interactive limit")
    return clean, total, invalid, duplicate


def profile_csv(text: str) -> tuple[list[Row], DatasetProfile, str]:
    """Compute one bounded profile; scientific dependencies load on demand."""
    import duckdb
    import numpy as np
    import pandas as pd  # type: ignore[import-untyped]
    import polars as pl
    from scipy import stats  # type: ignore[import-untyped]

    rows, total, invalid, duplicate = clean_csv(text)
    frame = pd.DataFrame(rows)
    polars_frame = pl.DataFrame(rows).lazy()
    costs = np.asarray(frame["cost"], dtype=np.float64)
    reference = [
        ServiceAggregate(
            service=str(name),
            cost=float(group["cost"].sum()),
            requests=int(group["requests"].sum()),
        )
        for name, group in frame.groupby("service", sort=True)
    ]
    evidence: list[EngineEvidence] = []
    # No extensions, external URLs, paths, or user SQL are accepted. DuckDB owns
    # one in-memory registered relation for the lifetime of this call.
    with duckdb.connect(
        ":memory:", config={"threads": "1", "enable_external_access": "false"}
    ) as db:
        db.register("measurements", frame)
        for engine in ("pandas", "polars", "duckdb"):
            samples: list[float] = []
            aggregate: list[ServiceAggregate] = []
            for iteration in range(4):
                started = time.perf_counter_ns()
                if engine == "pandas":
                    grouped = frame.groupby("service", sort=True)[["cost", "requests"]].sum()
                    aggregate = [
                        ServiceAggregate(
                            service=str(name),
                            cost=float(item["cost"]),
                            requests=int(item["requests"]),
                        )
                        for name, item in grouped.iterrows()
                    ]
                elif engine == "polars":
                    grouped_pl = (
                        polars_frame.group_by("service")
                        .agg(pl.col("cost").sum(), pl.col("requests").sum())
                        .sort("service")
                        .collect()
                    )
                    aggregate = [
                        ServiceAggregate.model_validate(item) for item in grouped_pl.to_dicts()
                    ]
                else:
                    aggregate = [
                        ServiceAggregate(service=name, cost=cost, requests=count)
                        for name, cost, count in db.execute(
                            "SELECT service, sum(cost), sum(requests) FROM measurements "
                            "GROUP BY service ORDER BY service"
                        ).fetchall()
                    ]
                elapsed = (time.perf_counter_ns() - started) / 1_000_000
                if iteration:  # First run warms each engine; not included in percentiles.
                    samples.append(elapsed)
                equal = len(aggregate) == len(reference) and all(
                    actual.service == expected.service
                    and actual.requests == expected.requests
                    and math.isclose(actual.cost, expected.cost, rel_tol=1e-10, abs_tol=1e-6)
                    for actual, expected in zip(aggregate, reference, strict=True)
                )
                if not equal:
                    raise RuntimeError("aggregation engines disagree")
            evidence.append(
                EngineEvidence(
                    engine=engine,
                    version=version(engine),  # type: ignore[arg-type]
                    p50_ms=float(np.median(samples)),
                    p95_ms=float(np.percentile(samples, 95)),
                    repetitions=len(samples),
                    matches_reference=True,
                )
            )
    counts, edges = np.histogram(costs, bins=min(10, len(costs)))
    stddev = float(np.std(costs, ddof=1)) if len(costs) > 1 else 0.0
    ci = None
    if len(costs) > 1:
        margin = float(stats.t.ppf(0.975, df=len(costs) - 1) * stats.sem(costs))
        ci = [float(costs.mean()) - margin, float(costs.mean()) + margin]
    report = DatasetProfile(
        input_rows=total,
        valid_rows=len(rows),
        invalid_rows=invalid,
        duplicate_rows=duplicate,
        service_count=len(reference),
        cost_total=float(costs.sum()),
        cost_mean=float(costs.mean()),
        cost_median=float(np.median(costs)),
        cost_p95=float(np.percentile(costs, 95)),
        cost_stddev=stddev,
        mean_ci95=ci,
        histogram=[
            HistogramBucket(lower=float(edges[i]), upper=float(edges[i + 1]), count=int(count))
            for i, count in enumerate(counts)
        ],
        services=reference,
        engines=evidence,
        caveats=[
            "Invalid rows are excluded; duplicates kept once. No values are imputed.",
            "The mean interval assumes independence; service/time correlations can invalidate it.",
            "Three warm repetitions measure in-memory aggregation, excluding cleaning and I/O.",
            "Local timings are workload-specific and do not establish a universal engine winner.",
        ],
        generated_at=datetime.now(UTC),
    )
    return rows, report, hashlib.sha256(text.encode("utf-8")).hexdigest()
