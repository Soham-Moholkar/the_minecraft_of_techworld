"""Authenticated local streaming operations with fixed tenant/topic selection."""

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from prometheus_client import Counter

from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.kafka_broker import KafkaBroker
from atlas_api.streaming import (
    Broker,
    ConsumeRequest,
    IngestRequest,
    LocalBroker,
    StreamConflict,
    StreamRead,
    UsageStream,
)
from atlas_api.streaming_export import export_parquet
from atlas_api.usage_lakehouse import LakehouseRead, refresh_lakehouse

router = APIRouter(prefix="/v1/streaming/usage", tags=["streaming"])
logger = structlog.get_logger()
OPERATIONS = Counter(
    "atlas_streaming_operations_total",
    "Bounded usage operations",
    ["provider", "operation", "status"],
)


def stream_resources(
    principal: Annotated[Principal, Depends(require_principal)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[tuple[UsageStream, Broker]]:
    """Open request-scoped resources; no credentials or raw failures cross HTTP.

    This profile is trusted local development only. The existing dev identity is
    insufficient for shared deployments; environment gating fails closed there.
    """
    if "owner" not in principal.roles:
        raise HTTPException(403, "owner role required")
    if settings.environment != "development" or not settings.streaming_enabled:
        raise HTTPException(403, "local streaming is disabled")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", principal.organization_slug):
        raise HTTPException(403, "invalid tenant")
    sink: UsageStream | None = None
    broker: Broker | None = None
    try:
        sink = UsageStream(
            Path(settings.streaming_store), principal.organization_slug, settings.streaming_provider
        )
        broker = (
            LocalBroker(sink.db, principal.organization_slug)
            if settings.streaming_provider == "sqlite"
            else KafkaBroker(settings.kafka_bootstrap, principal.organization_slug)
        )
        yield sink, broker
    except (HTTPException, RequestValidationError):
        raise
    except StreamConflict:
        raise HTTPException(409, "event conflict or local storage quota reached") from None
    except Exception:
        # SDK exceptions may contain broker addresses or raw payload; redact them.
        OPERATIONS.labels(settings.streaming_provider, "connection", "unavailable").inc()
        logger.warning("usage_stream_unavailable", provider=settings.streaming_provider)
        raise HTTPException(503, "usage stream unavailable; no automatic offset reset") from None
    finally:
        try:
            if broker:
                broker.close()
        except Exception:
            logger.warning("usage_stream_close_failed")
        if sink:
            sink.close()


Resources = Annotated[tuple[UsageStream, Broker], Depends(stream_resources)]


def record_operation(sink: UsageStream, operation: str, result: StreamRead) -> StreamRead:
    OPERATIONS.labels(sink.provider, operation, "ok").inc()
    logger.info(
        "usage_stream_operation",
        provider=sink.provider,
        operation=operation,
        processed=result.processed,
        lag=sum(p.lag for p in result.partitions),
    )
    return result


@router.get("", response_model=StreamRead)
def snapshot(resources: Resources) -> StreamRead:
    sink, broker = resources
    return record_operation(sink, "snapshot", sink.snapshot(broker))


@router.post("/events", response_model=StreamRead)
def ingest(payload: IngestRequest, resources: Resources) -> StreamRead:
    sink, broker = resources
    broker.publish(payload.events)
    return record_operation(sink, "publish", sink.snapshot(broker))


@router.post("/consume", response_model=StreamRead)
def consume(payload: ConsumeRequest, resources: Resources) -> StreamRead:
    sink, broker = resources
    return record_operation(sink, "consume", sink.consume(broker, payload.limit))


@router.get("/export", response_class=Response)
def export(resources: Resources) -> Response:
    sink, _ = resources
    content, digest = export_parquet(sink)
    OPERATIONS.labels(sink.provider, "export", "ok").inc()
    logger.info("usage_stream_export", provider=sink.provider, bytes=len(content))
    return Response(
        content,
        media_type="application/vnd.apache.parquet",
        headers={
            "Content-Disposition": 'attachment; filename="atlas-usage.parquet"',
            "Cache-Control": "no-store",
            "X-Atlas-Content-SHA256": digest,
        },
    )


@router.post("/lakehouse", response_model=LakehouseRead)
def publish_lakehouse(
    resources: Resources,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LakehouseRead:
    if not settings.lakehouse_enabled:
        raise HTTPException(403, "local lakehouse is disabled")
    sink, _ = resources
    result = refresh_lakehouse(sink, Path(settings.lakehouse_store))
    OPERATIONS.labels(sink.provider, "lakehouse", "ok").inc()
    logger.info("usage_lakehouse_refresh", rows=result.rows, changed=result.changed)
    return result
