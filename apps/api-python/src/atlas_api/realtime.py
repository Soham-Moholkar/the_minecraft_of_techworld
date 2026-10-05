"""Small process-local primitives for the first realtime protocol boundary.

The ticket store is intentionally an adapter-sized object. A single API process does
not need Redis merely to authenticate a WebSocket, while the interface makes the
future shared-store requirement explicit when ATLAS begins horizontal scaling.
"""

import secrets
import threading
import time
from collections import deque
from dataclasses import dataclass

from atlas_api.auth import Principal


@dataclass(frozen=True, slots=True)
class TicketGrant:
    principal: Principal
    expires_at: float


class RealtimeTicketStore:
    """Issue opaque grants and atomically consume each grant at most once."""

    def __init__(self) -> None:
        self._grants: dict[str, TicketGrant] = {}
        # Ticket issue happens in worker threads while redemption happens on the
        # event loop, so a regular lock protects both execution contexts.
        self._lock = threading.Lock()

    def issue(self, principal: Principal, *, ttl_seconds: int) -> str:
        now = time.monotonic()
        token = secrets.token_urlsafe(32)
        with self._lock:
            self._remove_expired(now)
            self._grants[token] = TicketGrant(
                principal=principal,
                expires_at=now + ttl_seconds,
            )
        return token

    def redeem(self, token: str) -> Principal | None:
        """Consume a grant before returning it, preventing connection replay."""

        now = time.monotonic()
        with self._lock:
            grant = self._grants.pop(token, None)
            self._remove_expired(now)
        if grant is None or grant.expires_at <= now:
            return None
        return grant.principal

    def _remove_expired(self, now: float) -> None:
        expired = [token for token, grant in self._grants.items() if grant.expires_at <= now]
        for token in expired:
            del self._grants[token]


class ConnectionCapacity:
    """Provide one atomic connection budget across all event-loop tasks."""

    def __init__(self) -> None:
        self._active = 0
        self._lock = threading.Lock()

    def acquire(self, *, maximum: int) -> bool:
        with self._lock:
            if self._active >= maximum:
                return False
            self._active += 1
            return True

    def release(self) -> None:
        with self._lock:
            # The guard makes cleanup idempotent if a future framework lifecycle
            # change causes an already-closed connection to be finalized twice.
            self._active = max(0, self._active - 1)


class SlidingWindowRateLimiter:
    """Bound messages per connection without a background cleanup task."""

    def __init__(self, *, maximum: int, window_seconds: float) -> None:
        self.maximum = maximum
        self.window_seconds = window_seconds
        self._timestamps: deque[float] = deque()

    def allow(self) -> bool:
        now = time.monotonic()
        boundary = now - self.window_seconds
        while self._timestamps and self._timestamps[0] <= boundary:
            self._timestamps.popleft()
        if len(self._timestamps) >= self.maximum:
            return False
        self._timestamps.append(now)
        return True
