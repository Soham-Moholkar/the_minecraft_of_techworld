"""Durable AI budget accounting and bounded in-process SLO evidence."""

from __future__ import annotations

import math
import threading
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas_api.config import Settings
from atlas_api.models import AIUsageReservation, Organization
from atlas_api.repository_ai import ProviderResult, RepositoryExplainRequest, SourceSlice

MICRO_USD = 1_000_000
HOSTED_PRICES_PER_MILLION = {
    "gpt-5.6-luna": (0.20, 1.20),
    "gpt-5.6-terra": (2.00, 12.00),
}


class AIBudgetExceeded(RuntimeError):
    """A conservative reservation would exceed the tenant's monthly limit."""


class AIBudgetSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monthly_limit_usd: float = Field(gt=0)
    committed_usd: float = Field(ge=0)
    reserved_usd: float = Field(ge=0)
    remaining_usd: float = Field(ge=0)


class AISLOSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_count: int = Field(ge=0, le=500)
    availability: float | None = Field(default=None, ge=0, le=1)
    p95_seconds: float | None = Field(default=None, ge=0)
    availability_target: float = Field(gt=0, le=1)
    p95_seconds_target: float = Field(gt=0)
    availability_met: bool | None
    latency_met: bool | None


class AIOperationsSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    budget: AIBudgetSnapshot
    slo: AISLOSnapshot


@dataclass(frozen=True)
class _SLOEvent:
    outcome: Literal["success", "failure"]
    duration_seconds: float


class AISLOTracker:
    """A process-local rolling window; Prometheus remains the durable telemetry path."""

    def __init__(self) -> None:
        self._events: deque[_SLOEvent] = deque(maxlen=500)
        self._lock = threading.Lock()

    def record(self, outcome: Literal["success", "failure"], duration_seconds: float) -> None:
        with self._lock:
            self._events.append(_SLOEvent(outcome, max(0.0, duration_seconds)))

    def snapshot(self, settings: Settings) -> AISLOSnapshot:
        with self._lock:
            events = tuple(self._events)
        if not events:
            return AISLOSnapshot(
                sample_count=0,
                availability=None,
                p95_seconds=None,
                availability_target=settings.ai_slo_availability_target,
                p95_seconds_target=settings.ai_slo_p95_seconds_target,
                availability_met=None,
                latency_met=None,
            )
        availability = sum(item.outcome == "success" for item in events) / len(events)
        durations = sorted(item.duration_seconds for item in events)
        p95 = durations[max(0, math.ceil(len(durations) * 0.95) - 1)]
        return AISLOSnapshot(
            sample_count=len(events),
            availability=round(availability, 6),
            p95_seconds=round(p95, 6),
            availability_target=settings.ai_slo_availability_target,
            p95_seconds_target=settings.ai_slo_p95_seconds_target,
            availability_met=availability >= settings.ai_slo_availability_target,
            latency_met=p95 <= settings.ai_slo_p95_seconds_target,
        )


ai_slo_tracker = AISLOTracker()


def _month_start() -> datetime:
    now = datetime.now(UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _costs(
    records: list[AIUsageReservation], settings: Settings
) -> tuple[int, int]:
    committed = sum(
        record.actual_cost_microusd for record in records if record.status == "completed"
    )
    fresh_after = datetime.now(UTC) - timedelta(seconds=settings.ai_reservation_ttl_seconds)
    reserved = 0
    for record in records:
        created_at = record.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        if record.status == "reserved" and created_at >= fresh_after:
            reserved += record.reserved_cost_microusd
    return committed, reserved


def budget_snapshot(
    session: Session, organization_id: object, settings: Settings
) -> AIBudgetSnapshot:
    records = list(
        session.scalars(
            select(AIUsageReservation).where(
                AIUsageReservation.organization_id == organization_id,
                AIUsageReservation.created_at >= _month_start(),
            )
        ).all()
    )
    committed, reserved = _costs(records, settings)
    limit = round(settings.ai_monthly_budget_usd, 6)
    used = (committed + reserved) / MICRO_USD
    return AIBudgetSnapshot(
        monthly_limit_usd=limit,
        committed_usd=round(committed / MICRO_USD, 6),
        reserved_usd=round(reserved / MICRO_USD, 6),
        remaining_usd=round(max(0.0, limit - used), 6),
    )


def reserve_budget(
    session: Session,
    organization: Organization,
    request: RepositoryExplainRequest,
    source: SourceSlice,
    settings: Settings,
    created_by: str,
) -> AIUsageReservation:
    # Serialize reservations through the tenant row. The lock is committed before
    # the network call, so slow inference never holds a database transaction open.
    locked = session.scalar(
        select(Organization).where(Organization.id == organization.id).with_for_update()
    )
    if locked is None:
        raise AIBudgetExceeded("organization is unavailable")
    hosted_possible = request.provider == "openai" or (
        request.provider == "auto" and settings.openai_api_key is not None
    )
    reserved_microusd = 0
    if hosted_possible:
        model = (
            settings.ai_economy_model
            if request.tier == "economy"
            or (request.tier == "auto" and request.intent == "explain")
            else settings.ai_balanced_model
        )
        input_price, output_price = HOSTED_PRICES_PER_MILLION.get(model, (0.0, 0.0))
        # One character per token is deliberately conservative for arbitrary code.
        # The configured floor covers custom models whose pricing ATLAS cannot know.
        input_ceiling = len(source.numbered_source) + sum(map(len, source.repository_map))
        estimated = (input_ceiling * input_price + 16_000 * output_price) / MICRO_USD
        reserved_microusd = round(
            max(settings.ai_run_reservation_usd, estimated) * MICRO_USD
        )
    current = budget_snapshot(session, organization.id, settings)
    if current.remaining_usd * MICRO_USD < reserved_microusd:
        session.rollback()
        raise AIBudgetExceeded("monthly repository AI budget exhausted")
    record = AIUsageReservation(
        organization_id=organization.id,
        status="reserved",
        provider_requested=request.provider,
        reserved_cost_microusd=reserved_microusd,
        actual_cost_microusd=0,
        input_tokens=0,
        output_tokens=0,
        created_by=created_by,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def settle_budget(record: AIUsageReservation, result: ProviderResult) -> None:
    record.status = "completed"
    record.provider_used = result.provider
    record.model = result.model
    record.actual_cost_microusd = round(result.estimated_cost_usd * MICRO_USD)
    record.input_tokens = result.input_tokens
    record.output_tokens = result.output_tokens
    record.completed_at = datetime.now(UTC)


def fail_budget(record: AIUsageReservation) -> None:
    record.status = "failed"
    record.completed_at = datetime.now(UTC)
