# ADR-0003: tenant authorization and audit evidence share the data boundary

- Status: accepted
- Date: 2026-08-27

Every project, note, search, and audit query joins through the organization selected
by the authenticated principal. Cross-tenant identifiers produce the same 404 as an
unknown identifier. This makes tenant scope a repository invariant instead of a UI
filter.

Sensitive mutations add their immutable audit event to the same SQLAlchemy session
and commit once. A rollback therefore removes both product state and audit evidence.
An outbox may later deliver these events externally without weakening this local
transactional guarantee.
