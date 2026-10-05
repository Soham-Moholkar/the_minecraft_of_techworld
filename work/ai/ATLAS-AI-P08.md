# ATLAS-AI-P08 — LLM and AI engineering

Status: complete. Owner: AI Platform. Roadmap: Phase 8.

Completed foundation: allowlisted repository catalog, bounded source reader,
OpenAI Responses provider, Luna/Terra cost routing, strict line explanation
schema, side-by-side source UI, authorization, audit, metrics, Docker source
snapshot, tests and explicit no-key failure behavior.

Completed provider portability: operator-configured local OpenAI-compatible Chat
Completions adapter, hosted/local readiness comparison, automatic and explicit
provider routing, normalized SSE deltas, final structured-output validation,
stream audit/metrics, streaming BFF and progressive UI evidence. Provider URLs
and model IDs remain configuration-only; browser callers receive no credentials,
endpoint details, tools or repository write authority.

Completed prompt lifecycle: append-only tenant prompt revisions with server-
assigned versions, owner-only creation, 100-version quota, audit evidence,
cross-tenant denial, reusable prompt selection in streamed runs, migration 0007,
and same-origin UI/BFF validation. Inline drafts remain available without being
silently persisted.

Completed retrieval and evaluation: request-local bounded indexing over at most
400 allowlisted files, 4 MB and 2,000 overlapping chunks; deterministic lexical
and signed feature-hashing embedding scores; hybrid reranking; stable citations
containing path, line range, content hash and citation ID; source-content prompt-
injection signals; and exact citation reuse in the UI. A fixed grounding,
citation-accuracy and injection regression suite persists immutable tenant-
scoped evidence behind owner authorization, quotas, audit events and metrics.

Completed operational hardening: tenant-scoped monthly budget reservations are
committed before hosted calls, settled to actual provider-reported usage, and
released after failures or stale-process TTL expiry. Content-addressed retrieval
chunks use a bounded thread-safe LRU and invalidate on source SHA changes. Auto
routing may fall back from hosted to an explicitly enabled local adapter only
when hosted inference fails before a response or first stream delta; explicit
provider selections never fall back. The workspace exposes remaining budget and
a bounded rolling availability/p95 SLO window, while Prometheus records runs,
latency, tokens, fallback and retrieval cache outcomes.

Acceptance:

- Embeddings, chunking, hybrid retrieval, citations and reranking: complete.
- Grounding, citation accuracy and prompt-injection evaluations: complete.
- Budget enforcement, cached context, provider fallback and operational SLOs:
  complete.
- Patch/write tools remain outside Phase 8. Phase 9 requires explicit approval.

Next implementation: Phase 9 may introduce narrowly scoped, human-approved patch
proposals and tool execution. It must preserve the read-only Phase 8 path and is
not authorized by this work item.
