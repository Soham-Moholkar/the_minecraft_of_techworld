# ADR 0011 — Bounded operator-managed agent memory

Date: 2026-10-01. Status: accepted. Work item: ATLAS-AI-P09.

## Decision

Add a tenant-owned operator memory store, separate from prompt versions, workflow
history, approvals and inference context. Owners in local development may create,
list and permanently delete plain-text notes at `/ai/repository`. Each note records
an operator-supplied provenance statement, creator, creation time and expiry. Provenance
is an assertion, not verified source evidence or a trusted instruction.

Inputs are bounded to a 120-character title, 2,000-character note and 240-character
provenance. Retention choices are 1, 7 or 30 days, default 7. Creation requires an explicit
no-secrets/no-approvals attestation. Conservative detection rejects recognizable credential
assignments, bearer/API/private keys, credential-bearing URLs, approval phrases/field names
and 64-hex digests. This is best-effort detection, not comprehensive DLP; operators must
not store sensitive/personal/confidential data. Obfuscated or unusual secrets can escape
detection. There is no encryption-at-rest or public/multi-user deployment claim.

The `automatic_context=false` contract is literal and checked by API/BFF/UI. Neither
inference, retrieval, workflow replay nor the MCP catalog imports/consumes this store.
Notes are never commands, authority, approvals or automatically injected model context.
There is no edit endpoint: replace by explicitly deleting and creating a new record.

## Quota, transaction and deletion boundaries

Migration 0015 adds `agent_memories`. Unique `(organization_id, slot)` and a slot range
check 1–50 enforce the tenant quota even when concurrent requests choose the same slot.
PostgreSQL parent-row locks serialize saves/cleanup. SQLite does not provide that row
lock; uniqueness/check constraints and write conflicts fail closed. Conflicts are visible,
not automatically retried with potentially duplicate writes.

GET filters out `expires_at <= now` without modifying storage. The browser drops expired
notes from its open snapshot with a bounded timer and no API polling. Physical cleanup
is demand-driven: a successful save purges expired tenant rows in the same transaction;
an owner can explicitly remove expired notes without creating another note. No unattended
retention daemon has been added. Idle tenants' expired rows remain stored until cleanup.

Explicit deletion names an owned UUID and requires `DELETE MEMORY`; the UI asks for a
second deliberate action. Cross-tenant/unknown identifiers return 404. Note lifecycle
and content-free audit commit together. Audit records contain identifiers/action/actor
only, never title, content, provenance or content hashes. Row deletion is not secure
erasure of SQLite pages, database logs, snapshots or backups; backup retention is a later
operational policy, and the UI/runbook state this limitation.

## API/UI and operations

`GET/POST /v1/ai/repository/memory`, `DELETE /memory/{memory_id}` and
`POST /memory/purge-expired` require authentication, owner role, existing organization
and development environment. No patch/test enablement is required or granted.
No-store BFF routes use a server-only fixed upstream, strict schemas, UUID/origin/body
validation, timeout and sanitized errors; upstream rejected-input bodies are not forwarded.
The UI keeps drafts only in component memory, renders escaped text rather than HTML or
Markdown, and handles unavailable services, conflicts, rejected drafts, expiry and cleanup.
Structured logs and fixed-label action counters contain no note text.

Next.js enforces the shared proxy's `server-only` marker at production compilation;
Vitest alone aliases that compiler marker to a test-only empty module. This does not
relax the production boundary or introduce a dependency.

## Verification and next slice

API tests cover lifecycle/audit privacy, secret/approval rejection, bounds/attestation,
local auth/owner/tenant access, strict expiry equality, tenant cleanup, quota/slot constraints,
save-time cleanup and telemetry. A disposable SQLite database passes migration upgrade,
downgrade to 0014 and re-upgrade with real memory persistence. UI/BFF tests cover deliberate
save/delete, origin/UUID/size/authority rejection, response redaction, inert text, retry and
open-page expiry. Live PostgreSQL locking remains an unavailable Docker-backed check.

Next: a resettable local agent-security lab for memory poisoning and approval-boundary
regressions with deterministic evidence. It must not invoke real tools, expose a service,
store credentials or broaden the existing model/worker authority.
