"""Redis cache-aside adapter for a bounded tenant project portfolio summary."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_api.models import Organization, Project
from atlas_api.schemas import CacheStatusCount, DatabaseCacheProfileRead

CACHE_TTL_SECONDS = 30
RedisDocument = dict[str, Any]
RedisFactory = Callable[[str], Redis]


class _CachedPortfolio(BaseModel):
    """Strict internal cache payload; poisoned or stale shapes fail closed."""

    model_config = ConfigDict(extra="forbid", strict=True)

    project_total: int = Field(ge=0)
    status_counts: list[CacheStatusCount] = Field(max_length=12)

    @model_validator(mode="after")
    def consistent_counts(self) -> _CachedPortfolio:
        """Reject inconsistent aggregates instead of displaying poisoned data."""
        statuses = [item.status for item in self.status_counts]
        if len(statuses) != len(set(statuses)) or self.project_total != sum(
            item.count for item in self.status_counts
        ):
            raise ValueError("inconsistent portfolio counts")
        return self


def _default_client(url: str) -> Redis:
    return Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=15,
    )


def tenant_cache_key(organization_slug: str) -> str:
    """Derive a non-enumerable, fixed-prefix key from the authenticated tenant."""

    digest = hashlib.sha256(organization_slug.encode("utf-8")).hexdigest()[:24]
    return f"atlas:cache:portfolio:{digest}"


class RedisProjectCacheRepository:
    """Read a Redis cache when healthy and always fall back to relational data."""

    def __init__(
        self,
        session: Session,
        redis_url: str | None,
        *,
        client_factory: RedisFactory = _default_client,
    ) -> None:
        self.session = session
        self.redis_url = redis_url
        self.client_factory = client_factory

    def _authoritative_summary(self, organization_slug: str) -> _CachedPortfolio:
        rows = self.session.execute(
            select(Project.status, func.count(Project.id))
            .join(Organization)
            .where(Organization.slug == organization_slug)
            .group_by(Project.status)
            .order_by(Project.status)
        ).all()
        counts = [CacheStatusCount(status=str(status), count=int(count)) for status, count in rows]
        return _CachedPortfolio(
            project_total=sum(item.count for item in counts),
            status_counts=counts,
        )

    @staticmethod
    def _read_cached(raw: object) -> _CachedPortfolio | None:
        if not isinstance(raw, (str, bytes, bytearray)):
            return None
        try:
            payload = json.loads(raw)
            if not isinstance(payload, Mapping):
                return None
            return _CachedPortfolio.model_validate(payload)
        except (json.JSONDecodeError, UnicodeDecodeError, ValidationError):
            return None

    def read(self, *, organization_slug: str) -> DatabaseCacheProfileRead:
        """Return hit/miss evidence without making product reads depend on Redis."""

        now = datetime.now(UTC)
        if self.redis_url is None:
            summary = self._authoritative_summary(organization_slug)
            return self._response(summary, "unavailable", "bypass", 0, now)

        client = None
        try:
            # URL parsing/client construction can fail too; cache configuration
            # must never turn an otherwise valid relational read into a 500.
            client = self.client_factory(self.redis_url)
            client.ping()
            key = tenant_cache_key(organization_slug)
            cached = self._read_cached(client.get(key))
            if cached is not None:
                remaining = client.ttl(key)
                ttl = remaining if isinstance(remaining, int) and remaining > 0 else 0
                if ttl > 0:
                    return self._response(cached, "available", "hit", ttl, now)

            summary = self._authoritative_summary(organization_slug)
            client.set(key, summary.model_dump_json(), ex=CACHE_TTL_SECONDS)
            return self._response(summary, "available", "miss", CACHE_TTL_SECONDS, now)
        except (RedisError, OSError, ValueError, TypeError):
            # Driver failures can contain endpoints and ACL details. The public
            # contract degrades to authoritative SQL with one generic state.
            summary = self._authoritative_summary(organization_slug)
            return self._response(summary, "unavailable", "bypass", 0, now)
        finally:
            try:
                if client is not None:
                    client.close()
            except (RedisError, OSError):
                pass

    @staticmethod
    def _response(
        summary: _CachedPortfolio,
        status: Literal["available", "unavailable"],
        cache_state: Literal["hit", "miss", "bypass"],
        ttl_seconds: int,
        generated_at: datetime,
    ) -> DatabaseCacheProfileRead:
        return DatabaseCacheProfileRead(
            status=status,
            cache_state=cache_state,
            project_total=summary.project_total,
            status_counts=summary.status_counts,
            ttl_seconds=ttl_seconds,
            consistency_model=(
                "PostgreSQL/SQLite authoritative; Redis cache-aside entries "
                "expire after 30 seconds."
            ),
            notes=[
                "A cache failure bypasses Redis and preserves the relational result.",
                (
                    "Keys are derived server-side from the authenticated tenant "
                    "and never accepted from callers."
                ),
            ],
            generated_at=generated_at,
        )
