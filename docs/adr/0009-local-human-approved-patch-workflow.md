# ADR 0009 — Local human-approved patch workflow

Status: accepted, 2026-09-23.

## Decision

Phase 9 begins with an opt-in, local-operator-only patch workflow. A caller proposes
one bounded replacement in one existing allowlisted UTF-8 source file. ATLAS reads the
authoritative bytes, validates the resulting syntax where deterministic, generates the
unified diff, and stores an immutable digest over path, before/after hashes, range,
summary, and rationale. Approval must repeat that exact digest. Application fails if
the source hash changed and uses a same-directory atomic replacement followed by a
hash verification. Rollback is allowed only while the current hash still equals the
applied hash.

The model receives no filesystem, shell, network, Git, test, commit, push, dependency,
or deployment tool. File creation, deletion, binary files, symlinks, dotfiles, lockfiles,
and paths outside reviewed prefixes are denied. The capability defaults off through
`ATLAS_AI_PATCH_TOOLS_ENABLED` and also fails closed outside the development environment.

A persisted framework-free state machine records `submitted → validating →
awaiting_approval` before a proposal becomes actionable. It accepts only the same typed
change-plan contract used by the guarded gateway. Invalid and stale plans become durable
`failed` or `conflicted` evidence; they do not disappear as transient HTTP errors. Patch
approval remains a separate mutation, and the workflow observes application/rollback
results through the proposal identifier. The transition graph cannot skip human review.

Test execution is an independently approved capability. A request selects only a
source-defined, versioned profile; the immutable run digest binds the patch digest,
candidate hash, exact command, fixed image, working directory, environment and resource
policy. Approval queues durable work for a separate local worker. That worker stages the
candidate without mutating the checkout and runs it in a non-root Docker container with
`network=none`, a read-only mount, dropped capabilities, no-new-privileges, fixed
environment, and CPU, memory, swap, PID, wall-time and output limits. Docker/image
absence fails closed: host execution is never substituted.

Cancellation is durable for queued and running work. Heartbeats make abandoned runs
recoverable as `interrupted`, and output is persisted as a bounded excerpt plus a hash.
Neither a queued nor a passing test changes patch approval state, and active execution
blocks patch application to avoid testing and mutating the same candidate concurrently.

Linked deterministic workflows append test request, queue, start, cancellation and
terminal results as evidence events while retaining their existing authority state.
Evidence cannot invoke a transition or change `awaiting_approval` into `applied`.
An interrupted run is never requeued. An explicit retry creates a new record with a new
run ID, attempt number and digest bound to its predecessor, then returns to
`pending_approval`; the operator must approve that new digest before execution.

The workflow now routes through a versioned, source-owned graph. Its typed nodes name
the single guarded proposal tool, conditional edges name observed outcomes, and edges
out of human review or applied state declare their separate patch or rollback approval
boundary. Graph validation rejects ambiguous branches at startup. Every workflow row
pins the graph version; migration 0014 marks prior runs as version 1. A tenant-scoped,
read-only replay endpoint validates the stored transition and evidence sequence against
that graph before rendering it. Replay never executes a tool or grants authority.
Version 1 must remain available when the policy evolves, or older histories fail closed.

## Consequences

This produces a useful L4 human-approval boundary without claiming remote-agent
sandboxing. Database and filesystem changes cannot be one transaction, so `applying`
and `rolling_back` journal states are committed before I/O. Hashes make interrupted
operations diagnosable. Remote or multi-user execution requires OIDC, per-user isolated
workspaces, egress controls, resource quotas, and a new threat-model review.

See `security/threat-models/ATLAS_CODEX_CONTEXT_BUNDLE_V4-threat-model.md`.
