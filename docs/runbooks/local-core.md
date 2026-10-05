# Runbook: local core profile

Use the commands in the root `README.md`. A healthy core has PostgreSQL, API, and
web containers healthy; `/health` reports a reachable database; `/metrics` exposes
request counters and latency histograms; and the overview lists three deterministic
seed projects. Stop with `docker compose down`. Data is retained in the named volume.
Use `docker compose down -v` only when intentionally discarding local ATLAS data.

