# Usage BI

ATLAS owns a BI-only numeric projection and read-only observer for a fixed
Superset 6.1.0 dashboard. Publication metadata is distinct from dataset freshness.
Owner/development/independent opt-in, configured tenant/dashboard/JWT, strict
title/ID, byte caps and no redirects/proxies protect reads. SQL/owners/CSS/JSON
and credentials never enter the response. Native projection/permission tests pass;
the Linux image/login/dashboard and refresh workflow remain runtime-unverified.

## Projection

Set `ATLAS_PIPELINE_ENABLED=true`, `ATLAS_PIPELINE_API_URL` to the local streaming
API, `ATLAS_PIPELINE_API_TOKEN` to its existing owner credential and
`ATLAS_PIPELINE_TENANT=northstar`. Then run:

```powershell
.venv/Scripts/python.exe scripts/publish_usage_bi.py
```

The job downloads/validates accepted Parquet and transactionally replaces one
row in `artifacts/usage-bi/northstar/sqlite/usage.db`. Kafka has a separate provider
directory. `usage_rollup` contains tenant/provider, row count, units, digest and
refresh time. It copies no application tables, raw IDs, notes or secrets. Reruns
replace the aggregate rather than appending duplicates. Native tests exercise the
actual SQLAlchemy read-only URI, rejected writes and cross-tenant rejection.

## Local Superset

Configure a strong `ATLAS_SUPERSET_SECRET_KEY` (at least 32 characters) in ignored
operator configuration. No administrator/password is supplied by the profile;
it fails closed without the secret. CSRF/HttpOnly/SameSite remain enabled,
template/guest embedding is disabled, rows/resource use are bounded, the BI
projection is mounted read-only, and the listener is loopback 58088. Metadata
uses a separate named volume and local SQLite, not production persistence.

```powershell
docker compose -f compose.yaml -f infra/superset/compose.yaml --profile bi config --quiet
docker compose -f compose.yaml -f infra/superset/compose.yaml --profile bi run --rm superset superset db upgrade
docker compose -f compose.yaml -f infra/superset/compose.yaml --profile bi run --rm superset superset fab create-admin
docker compose -f compose.yaml -f infra/superset/compose.yaml --profile bi run --rm superset superset init
docker compose -f compose.yaml -f infra/superset/compose.yaml --profile bi up -d superset
```

Choose local credentials interactively. In authenticated Superset, connect only
the BI dataset with this URI, create count/usage charts from `usage_rollup` and
name its dashboard exactly `ATLAS usage northstar`:

```text
sqlite:///file:/var/lib/atlas-bi/northstar/sqlite/usage.db?mode=ro&uri=true
```

Grant a dedicated observer access only to that dataset/dashboard. Configure its
access JWT in `ATLAS_SUPERSET_API_TOKEN`, the numeric ID in
`ATLAS_SUPERSET_DASHBOARD_ID` and `ATLAS_SUPERSET_ENABLED=true`, then recreate only
the API to load settings. An expired/missing credential displays unavailable.
The `/pipelines` card reports publication only. Rerun the publisher for fresh data
and inspect source digest/refresh time in the authenticated dashboard.

Keep the application database separate; preserve vendor protections and avoid
public/guest/global database grants. If the vendor's current security policy
rejects a connection, investigate it rather than bypassing it. Stop only Superset
after acceptance, preserving the named metadata volume and projection; no routine
`down -v`. Actual image/startup/login, role isolation, chart reads, refresh and
read-only mount/SQLite compatibility remain acceptance gates while Docker's
supported Linux engine is unavailable.

Official provenance: [6.1.0 release](https://github.com/apache/superset/releases/tag/6.1.0),
[dashboard API](https://github.com/apache/superset/blob/6.1.0/superset/dashboards/api.py),
[configuration](https://github.com/apache/superset/blob/6.1.0/superset/config.py).
The official image retains Apache-2.0 and upstream subcomponent notices.
