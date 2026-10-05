# ADR 0008: cost-aware, read-only repository intelligence

Accepted 2026-09-19. Phase 8 begins with a repository code-intelligence
vertical that preserves source formatting and renders explanations in a separate
column. ATLAS does not inject generated commentary between every source line:
doing so would fight formatters, inflate diffs and obscure the executable code.

The provider contract has two fixed OpenAI model routes. `gpt-5.6-luna` handles
high-volume line explanations; `gpt-5.6-terra` handles reviews and change plans.
The official model catalog describes Luna as cost-sensitive and Terra as the
intelligence/cost balance. Both expose a 1,050,000-token context window and
Responses structured outputs. At verification time their published text prices
were respectively $0.20/$1.20 and $2.00/$12.00 per million input/output tokens.
Model IDs remain environment-configurable for controlled migrations, but HTTP
callers can select only `economy`, `balanced`, or `auto`.

Repository access belongs to ATLAS, not the model. The API resolves paths beneath
an allowlisted source snapshot, blocks dotfiles, generated/vendor directories,
binary extensions and files over 256 KB, then reads at most 120 lines. The model
receives a repository path map and one numbered source slice as untrusted JSON
data. It receives no shell, filesystem, network, patch, or execution tool. Strict
structured output must account for every selected line. ATLAS reattaches the
original bytes after validation so generated text cannot masquerade as source.

The Responses request uses `store: false`, a hashed safety identifier, bounded
output and no tools. The OpenAI key is a `SecretStr`, enters through the API
environment only, and is absent from browser responses, logs, audit events and
the container source snapshot. Without a key, catalog browsing works and model
generation fails closed with 503.

Each successful run records path, intent, selected model, line count, token
counters, duration and a tenant-scoped audit event. Source text and model output
are not persisted. The displayed dollar value is an estimate based on the
verified public rates; provider billing remains authoritative.

This L1/L2 boundary is not yet a write-capable coding agent. Later Phase 8 work
adds local-provider parity, retrieval/embeddings, prompt/eval versioning and
grounded repository context. Phase 9 may add scoped tools and human-approved
patch application; write authority must never be inferred from explanation.

## Amendment: local parity and normalized streaming

ATLAS now supports an operator-enabled local OpenAI-compatible adapter using the
widely implemented Chat Completions streaming shape. The hosted adapter consumes
Responses API SSE events; the local adapter consumes Chat Completions SSE chunks.
Both emit one internal delta contract and must produce the same validated final
`ExplanationDraft` before the UI renders the authoritative side-by-side result.

The browser selects only `auto`, `openai`, or `local`. Base URLs, API keys and
model identifiers remain server configuration, preventing caller-controlled
network targets. Health checks expose only configured/reachable state, model name
and bounded latency—not URLs, credentials or upstream response bodies. Streaming
errors are redacted SSE events because HTTP status can no longer change after the
first response byte. Partial JSON is shown only as transient progress evidence;
it is never persisted or presented as a completed explanation.

Prompt instructions may be saved as append-only tenant revisions. ATLAS assigns
the next version while holding the tenant row, caps storage at 100 revisions per
tenant, and exposes no update/delete API. A streamed run resolves the referenced
prompt only inside the authenticated tenant before contacting a provider. Inline
instructions remain ephemeral, and prompt creation produces audit evidence.

Official references verified 2026-09-19:

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.6-luna
- https://developers.openai.com/api/docs/models/compare
- https://developers.openai.com/api/reference/cli/resources/responses/methods/create

## Amendment: bounded hybrid retrieval and evaluation evidence

Repository retrieval builds a fresh request-local index from the existing
allowlisted source reader. It is capped at 400 files, 4 MB and 2,000 chunks;
chunks contain 40 lines with an eight-line overlap. This intentionally avoids a
stale shared index at L4 and makes source-hash citations verifiable immediately.
Multi-tenant durable indexes and content-addressed cache invalidation remain L5.

Ranking combines normalized query-token overlap with a provider interface whose
first implementation is dependency-free signed feature hashing. The hashing
baseline is reproducible and offline, but is not represented as a learned
semantic embedding. The interface permits a learned local or hosted embedding
provider later without changing retrieval responses. Stable tie-breaking uses
score, path and start line. Each result contains an exact path, line range,
whole-file SHA-256, derived citation ID and source snippet.

Retrieved repository text is untrusted data. Rule-based prompt-injection checks
return rule identifiers rather than matched hostile content, and the search API
does not log the raw query. Only owners may retrieve source snippets or create an
evaluation. Fixed grounding, citation-integrity and injection fixtures create
append-only tenant evidence with a 100-record quota, audit event, counters and
latency histograms. No retrieval path grants tools, execution, network access or
write authority.

## Amendment: budgets, caching, fallback and SLOs

Before a hosted call, ATLAS locks the tenant row, measures current-month committed
and active reserved spend, and persists a conservative reservation. The estimate
uses the selected fixed model's verified rates, a one-character-per-token source
ceiling, the maximum output allowance and an operator-configured minimum. The
transaction commits before network I/O. Success replaces the reservation with
provider-reported actual usage; failure releases it. Reservations abandoned by a
process exit stop counting after a bounded TTL. Custom model operators must set a
reservation floor appropriate to their provider price.

Retrieval chunks are cached in a process-local, thread-safe LRU keyed by resolved
repository root, path and whole-file SHA-256. Every request still rebuilds the
allowlisted catalog, so a changed hash cannot reuse stale chunks. The cache is an
acceleration layer only: no correctness or authorization decision depends on it.

Auto routing can fall back from hosted inference to the local adapter only when
the local adapter is explicitly enabled and the hosted provider is unavailable.
Explicit provider selection never falls back. Streaming fallback is permitted
only before the first event; after a delta, mixing output from two providers would
violate provenance and therefore fails closed.

ATLAS exposes tenant budget state and a bounded 500-sample process-local window
for inference availability and p95 latency. Prometheus remains the scrapeable
telemetry path and adds fallback plus retrieval cache counters. The workspace
labels the rolling window honestly when no samples exist. These controls do not
grant either provider new tools or repository write authority.
