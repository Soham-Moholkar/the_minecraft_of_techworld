# Phase consistency audit — 2026-10-03

The historical Phase 0–8 completion records describe implemented local baselines.
They do not certify that every runtime is currently available or that every
advanced ecosystem capability exists. Phase 9 and Phase 10 remain in progress.
This audit checks cross-phase product claims, source metadata and repeatable
quality gates; it is not a complete security or production readiness review.

| Phase | Inconsistency / examination | Resolution |
| --- | --- | --- |
| 0 | Seeding checked slugs globally and failed to recover partial state | Tenant-scoped per-project checks; preserve existing edits; real persistence/idempotency regression |
| 0 | CI installed no streaming/lakehouse extras while strict typing imports Iceberg; optional tests could skip | Explicit extras, real usage runtime gate, Linux Kafka and Airflow parse jobs |
| 1 | Shell asserted Production/nominal systems and offered a nonfunctional organization switch | Honest development workspace label, service diagnostics link, inert identity display |
| 1 | Dashboard presented fixed availability, event/workload/security values, activity and SLO charts as live | Real validated health/project/audit requests; independent failure states; dated quality evidence; fabricated data removed |
| 1 | Inventory badges asserted services operational/verified and static counts implied runtime checks | Source inventory labels, stale counts removed; runtime/verification distinguished |
| 2 | Python progression/lifecycle metadata | Revalidate actual mastery lab and manifest contracts in quality profile |
| 3 | Project/note BFF mutations lacked origin validation and request bounds; provider JSON/errors passed through | Same-origin guards, streamed byte caps, strict inputs, UUID paths, typed outputs, redacted failures and no-store; six web regressions |
| 4 | Earlier database runtime failures were mixed with local acceptance; provider identifiers inconsistent | Explicit not_run runtime gates; registry GraphQL/gRPC/Compose identifiers aligned; no Docker pass claim |
| 5 | Data science evidence/registry/profile consistency | Revalidate real dirty-data/scaling lab and API suite; no new runtime claim |
| 6 | ML evaluation evidence/profile consistency | Revalidate real training/evaluation and bounded API tests/lab |
| 7 | TensorFlow/Keras hidden under a PyTorch progression row | Independent source-backed rows; revalidate actual framework/applied-AI labs |
| 8 | Responses provider displayed L6 although its registry level is L3; retrieval/operations lacked distinct display | Provider corrected to L3; independent hybrid retrieval L4 and operations L6 rows |
| 9 | Patch child routes mixed `[id]` and `[proposalId]`, crashing Next server startup despite successful build | Normalize to `[id]`, add route-structure gate, recheck actual server |
| 9 | Claimed continuation security lab absent | Resettable actual memory/approval/workflow policy exercise, seven rejected attempts, lifecycle/CI/catalog coverage |
| 10 | Container usage/catalog state was disposable despite durable product behavior | Named usage/Kafka volumes and non-root usage directory; live persistence verification pending |
| Cross-phase | Test center snapshot dated September 21 and omitted new gates | Portable profiled runner, explicit passed/failed/not_run, raw outputs excluded from browser snapshot; newly recorded evidence |
| Cross-phase | Progress/registry/displayed levels could silently drift | `scripts/audit_consistency.py` validates unique IDs, source paths, progress identifiers and displayed levels; local/CI gate |
| Cross-phase | Development credentials protected no host network boundary; database/API/web ports bound all interfaces | Loopback-only Compose ports; consistency gate checks every source-owned profile |
| 10 | Spark/Hadoop encoded workspace spaces twice | Actual local JVM acceptance caught the failure; use Hadoop path strings and explicit child-process SPARK_HOME; rerun passed |

Source inspection and focused regressions pass. Final aggregate quality results
are stored in `apps/web/src/data/quality-snapshot.json` and CHECKPOINT.md.
Spark local JVM and actual browser acceptance now pass. The audit does not promote
unverified standalone Spark/Flink, Superset, remote lakehouse features,
multi-agent behavior, MCP transport or Docker-backed gates.
No store/volume reset, deployment, push or commit was performed.

## Continuation — 2026-10-04

Superset now has a real aggregate-only SQLite projection, native read-only
connection tests and tenant-bound publication observations. Container/chart/role
acceptance remains pending. Spark, Flink and BI source locations are available to
the curated repository reader; its vendor `.tools` exclusion is regression-tested.
Docker build context excludes the portable JRE and generated verification output.

The full API suite passed 188 tests with coverage above the required 80 percent.
The aggregate runner's former 300-second API deadline was shorter than the full
suite's combined framework cold-start budget. The observed suite took 321.69s;
the aggregate gate now allows 600s while retaining individual worker limits.
Final fresh profile evidence and browser results are recorded in CHECKPOINT.md and
the dated quality snapshot, without promoting unavailable Linux runtime gates.

Final recovery snapshot: **23 passed, 0 failed, 6 not_run** on 2026-10-04.
Fresh verification includes 110 frontend tests / 43 files, 188 API tests, strict
mypy across 47 source files, Node protocols and every selected local lab.
Windows acceptance teardown now ends only its still-live owned interpreter tree
and retries transient sharing violations. Actual newest pipeline browser checks
passed current Spark data, refresh controls and disabled provider states, with no
console errors; the production Test Center shows the same passed snapshot.
Screenshots and logs remain under `output`; temporary services were stopped.

The operational canvas now lets an operator inspect topic/retention, accepted
effects, Parquet lineage and actual current/older Spark receipts in one fixed
topology. Other branches are explicitly source-defined; selecting or refreshing
never consumes, submits a job, publishes snapshots or modifies BI. Independent
contract-validated reads and cancelled mounts are regression-tested. Test Center
now displays each gate's original check time, separate from snapshot generation.

Streaming BFF admission previously checked size after eager body reads, and its
Parquet download did the same with binary buffers. Both now share incremental
byte caps, cancel oversized/error bodies and prohibit redirects with server
credentials. Four regressions cover cancellation, forwarding refusal and binary
byte/header preservation. The allowed web origin remains explicit configuration;
a wrongly configured browser fixture was rejected, then corrected without relaxing
the origin check.

Final frontend evidence supersedes earlier counts: **119 tests / 46 files**,
lint/types/build/registry pass; overall snapshot remains 23 passed / zero failed /
six not_run. Actual browser processing moved lag 1→0 and accepted units 4→7;
the canvas correctly changed the original Spark receipt from current to older.
Per-gate dates remain visible and original API checks retain their timestamp.
Owned services, tabs and synthetic fixtures were removed; proof/logs are retained.
ADRs 0014/0015 now follow the existing `docs/adr` directory convention.
