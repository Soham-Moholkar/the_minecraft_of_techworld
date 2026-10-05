# ATLAS-PLAT-P11: Development infrastructure and cloud evolution

Status: in progress. User explicitly moved to Phase 11 on 2026-10-04;
Phase 9/10 acceptance stays unfinished.

First slice: source-owned Helm chart, separately retained namespace and SQLite PVC,
private API/web services, whole-object independent deployment policy, calculated
budget, owner/development read-only API, typed BFF and real Infrastructure workspace.
Refresh, contract findings and review-only teardown are functioning behavior.
Native Helm lint/render and unsupported override rejection run against the actual
toolchain; security/component tests and full quality gates provide local evidence.
Exact final counts and browser evidence live in CHECKPOINT.md.

Remaining acceptance: Docker builds, isolated local Kubernetes startup, supported
cluster/CNI verification, live namespace isolation, quotas, persistent recovery and
manual teardown/reconcile. Infrastructure source presence does not certify these.
Remaining phase: supported Linux/shell and Ansible acceptance, immutable container
releases, persistent IaC state governance, cloud provider comparison and actual
cost/teardown guards. Terraform remains an unimplemented alternative to OpenTofu.
Do not create paid cloud resources or expand application execution authority.

Implemented that next native slice: OpenTofu 1.13.0 builtin-only budget metadata,
whole-configuration allowlist, generated validated deployment input, isolated
environment/fixture, actual create/no-op/precondition/teardown and redacted atomic
receipt. Independent owner/development API/BFF/UI distinguish current, older,
missing and unavailable. Source scope/privacy regressions and CI job added.
Persistent state governance, cloud providers, Ansible and releases remain unfinished.

Acceptance completed 2026-10-05: 253 API tests, 128 frontend tests, 25 passing
platform gates, zero failed and six unrun runtime gates. Final production rebuild
and actual browser current/older/restored source lineage, disconnected/source-failure
evidence clearing and mobile layout pass. Original source bytes restored, receipt
retained, temporary services/database/tab removed. Remote CI and live cluster
acceptance remain unverified; see CHECKPOINT.md for exact commands and evidence.
