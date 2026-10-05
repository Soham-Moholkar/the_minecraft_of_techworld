# AI engineering progression

- L0: deterministic repository catalog and bounded source reader.
- L1: authenticated source explanation with exact line-to-comment alignment.
- L2: fixed cost router, strict structured output, prompt-injection boundary,
  audit, token/cost metrics and provider failure handling.
- L3 implemented: provider-neutral streaming, a local OpenAI-compatible runtime
  and immutable tenant prompt versions are integrated.
- L4 implemented: bounded overlapping chunks, lexical and deterministic local
  embedding adapters, hybrid reranking, exact hash/line citations, untrusted-
  instruction signals and persisted grounding/citation/injection evaluations.
- L5 implemented baseline: content-addressed bounded chunk caching and existing
  top-k context compaction avoid stale reuse and unbounded prompts. Durable
  multi-tenant/vector indexes and batching remain future scale work.
- L6 implemented baseline: durable tenant budget reservations, rolling SLO
  evidence, Prometheus telemetry, safe pre-stream provider failover, audit and
  fixed prompt-injection regression. Larger red-team corpora remain ongoing
  governance work rather than a prerequisite for the Phase 8 product boundary.
- L4 agent baseline implemented: local-only exact-diff proposals, immutable approval
  binding, guarded atomic writes, audit, and hash-safe rollback. The model remains
  tool-free. A persisted framework-free workflow now records submitted, validation,
  human-review, application and rollback outcomes without permitting approval bypass.
  Separately approved fixed test profiles now run candidate bytes through a fail-closed,
  networkless, read-only, resource-bounded Docker worker with durable evidence,
  cancellation and interrupted-run recovery. Test events now join the workflow timeline
  without changing its state, while retries create fresh lineage and require a new
  approval. Test success grants no mutation authority.
- L4 agent graph/replay slice: source-owned, schema-checked nodes and conditional
  edges route observed validation/application outcomes. Approval authority is explicit
  on privileged edges; stored graph version 1 preserves replay meaning. A read-only
  API/BFF/UI projects and verifies every persisted transition and test evidence event,
  rejecting unknown or reordered history without executing tools.
- L2 MCP discovery baseline: nine source-owned schemas and explicit scope/approval
  policy are inspectable through local owner-only API/BFF/UI. Discovery is read-only,
  has no transport or dispatcher, and never invokes tools even when local flags are on.
  The descriptor schema follows revision 2026-07-28; protocol conformance is not claimed.
- L3 operator-memory baseline: tenant ownership, immutable provenance/expiry metadata,
  50 database-bounded slots, best-effort secret/approval rejection, explicit deletion,
  demand-driven physical expiry cleanup, audit privacy and API/BFF/UI are implemented.
  Notes remain untrusted plain text and never enter inference or grant authority.
  Unattended retention and governed explicit context selection are later work.
- L7 remains planned for alternate retrieval and sandboxed remote coding architectures.

The active product lives at `/ai/repository`. It deliberately renders source and
commentary side by side instead of rewriting source with line-by-line comments.
See ADR 0008 for the security and cost boundary.
