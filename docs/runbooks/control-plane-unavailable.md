# Runbook: control plane unavailable

1. Request `GET /health` and capture `X-Request-ID`.
2. Inspect API structured logs for that identifier.
3. Run `docker compose ps`; PostgreSQL and API health checks must be healthy.
4. Run the Alembic current/upgrade commands from `README.md`.
5. If the database is unavailable, restore it before accepting mutations; do not
   enable an in-memory fallback because it would split authoritative state.
6. Verify recovery from the web dashboard and Prometheus request/error signals.

