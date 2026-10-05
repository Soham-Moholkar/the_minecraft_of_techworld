# ADR 0010 — Local, read-only MCP contract discovery

Date: 2026-10-01. Status: accepted. Work item: ATLAS-AI-P09.

## Decision

Add a source-owned catalog and operator explorer at `/ai/repository`. The authenticated
local-only `GET /v1/ai/repository/mcp/catalog` derives JSON Schema from the existing
Pydantic patch, workflow and test request models. Small inherited models add the UUID
parameters otherwise carried in REST paths. Nine descriptors are deterministically
ordered, with a versioned catalog and independent ATLAS scope/role/approval metadata.

This is MCP-shaped **contract discovery**, not an MCP server, SDK integration, transport
or tools/call endpoint. There is no dispatcher, user-defined URL, runtime registration,
tool execution, remote connection or multi-agent authority. `invocation_enabled` is
literally false at both API and browser validation boundaries. The existing REST
handlers remain the only enforcement boundary; schemas are not permission checks.

MCP tool descriptor shape and JSON Schema dialect were checked against the official
[2026-07-28 tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
on 2026-10-01. No external source implementation was copied and no SDK/dependency was
added. We deliberately do not advertise MCP transport conformance. ATLAS policy is
separate from MCP annotations because annotation hints must not grant authority.

## Safety and operations

Discovery requires a valid development principal, owner role and an existing organization;
non-development environments reject it. It may run while mutation flags are off.
Flag eligibility is presented separately from invocation, human approval and Docker health.
Discovery reads no files, creates no proposal/run/audit records and stores no tenant evidence.
The API emits a fixed-label counter and a structured read log; schemas and secrets are not
logged. API and BFF replies are no-store. The BFF uses a fixed authenticated upstream,
strict envelope validation, timeout and redacted errors. The browser renders inert,
escaped JSON and aborts obsolete reads; refresh clears stale policy information.

JSON Schema covers input shape only. Cross-field ordering, quotas, path allowlists,
source hashes, exact digest approvals, workflow states and sandbox availability remain
server-side checks. A future tool transport must implement those checks explicitly,
not infer authority from a catalog field or enabled flag.

## Verification and next complexity

Tests cover request-model/schema drift, UUID parameters, confirmation literals, flags,
auth/owner/organization/local restrictions, absence of mutation endpoints and side effects,
BFF redaction, invalid authority, duplicate names, loading/error/filter/refresh states,
and inert schema markup. Existing lifecycle tests remain authoritative for invocation.

Next add durable, tenant-scoped agent memory as operator-managed data with bounded
retention and explicit deletion. It must never persist secrets or approvals, automatically
alter model context, or create execution authority. MCP transport and remote workers remain
later, separately reviewed slices.
