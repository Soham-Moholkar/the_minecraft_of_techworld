# ADR 0014 — Bounded operator-owned usage compute

Status: accepted for trusted local development; runtime acceptance tracked separately.

The accepted-event API provides a fixed typed Parquet export with embedded lineage.
Spark is introduced as a real reader/aggregate behind that contract, rather than
duplicating broker consumption or granting the web application arbitrary SQL/job
authority. A source-owned operator job checks the entire bounded envelope and uses
actual Spark SQL to verify row/identity/unit aggregates before publishing a receipt.

Receipts are one fixed local file per tenant/provider, atomically replaced only
after successful aggregation. The read-only API validates namespace, schema,
bounds/time, source currency and current aggregates. Empty, stale and unavailable
are distinct UI states. Numeric structured events/fixed metrics avoid raw IDs,
credentials and filesystem paths. An exclusive job lock protects the shared input.

The optional standalone profile uses an internal network, no published Spark ports,
explicit CPU/memory/PID/core caps and a four-minute job deadline. The API mounts
receipt storage read-only. This is not production Spark identity or isolated
multi-user job execution. Local JVM and standalone acceptance are separate gates.
No existing database migration or stream-effect/checkpoint mutation is needed.

Spark/PySpark 4.2.0 official release, Apache-2.0 license, installation/security docs
and official image source were reviewed on 2026-10-03. Arrow remains pinned at
25.0.1. The native test runtime is a checksum-verified workspace-local Temurin JRE
21.0.12.1+1; its upstream license/notice remains with the ignored archive extraction.
See `docs/runbooks/usage-compute.md` for provenance, commands and exact limitations.

Flink 2.3.0 adds a source-owned bounded Table API batch alternative and fixed-job
read-only checkpoint/backpressure REST observations. Deprecated samples remain
unavailable; plans/configuration/paths and execution controls are excluded.
The configured tenant/owner, development opt-in, loopback listener and resource
caps preserve the operator boundary. Linux image/job/recovery acceptance remains
pending. Official image/PyPI ranges verified on 2026-10-04 require an isolated
Beam 2.61.0 / Arrow 16.1.0 graph, without downgrading API/Spark's Arrow 25.0.1.

The operational canvas is an owned, fixed topology over these contracts. Stage
selection only inspects boundaries and existing evidence; it cannot edit a DAG,
submit SQL/jobs, advance offsets or publish artifacts. Streaming and Spark reads
settle independently and expose older receipts explicitly. Other graph branches
remain source-defined until their separate provider observations are available.
This avoids introducing a second job-control authority through graph interaction.
