# 19 — Autonomous Execution, Completion and Checkpoint Protocol

## Objective

When Codex is instructed to build ATLAS, it must perform implementation work rather than repeatedly stopping to propose more plans.

The scope is intentionally enormous. Completion therefore means continuous execution through the roadmap, with durable checkpoints whenever platform/session/tool limits prevent further work in the current run.

## Core execution rule

> **Do not voluntarily stop after planning, scaffolding, one page, one service, or one milestone. After completing and verifying the current coherent slice, immediately continue with the next highest-priority incomplete item.**

Continue until:
- the entire currently defined ATLAS scope is implemented and verified, or
- an external/tool/session/resource limitation makes further execution impossible.

## If blocked by an implementation decision

Do not ask the user for ordinary architecture choices that can reasonably be resolved from the context.

Use:
1. existing ATLAS architecture,
2. official best practices,
3. stable maintained defaults,
4. the simplest extensible choice.

Record non-trivial decisions in an ADR.

Ask only when there is genuinely missing information that cannot safely or correctly be inferred.

## If blocked by unavailable credentials/cloud resources

Implement:
- local equivalent,
- interface/provider,
- mock or emulator where appropriate,
- documented environment variables,
- integration tests that can run without production credentials.

Do not halt the rest of ATLAS because one external provider is unavailable.

## If a session/tool/runtime limit forces a stop

Before stopping, create/update:

```text
CHECKPOINT.md
.atlas/progress.json
```

`CHECKPOINT.md` must include:

```text
Current roadmap phase
Last completed task
Files created/changed
Architecture decisions
Database migrations
Commands run
Tests passing
Tests failing
Known issues
Services currently expected to run
Uncommitted/partial work
Exact next task
Exact next command
```

`.atlas/progress.json` should be machine-readable:

```json
{
  "current_phase": "...",
  "last_completed_task": "...",
  "next_task": "...",
  "quality_gates": {
    "lint": "pass",
    "typecheck": "pass",
    "unit": "pass",
    "integration": "pass",
    "e2e": "not_run"
  },
  "blocked": false,
  "blocker": null
}
```

The next Codex run must read these files first and continue.

## Continuous build loop

Repeat:

1. read authoritative context,
2. inspect current repo/progress,
3. select next coherent item,
4. implement actual files/code/config/migrations/tests,
5. run format/lint/typecheck,
6. run relevant tests,
7. run/build the real product,
8. verify visible/API/data behavior,
9. verify security/observability requirements,
10. fix discovered failures,
11. update technology registry/provenance,
12. update ADR/work item/progress,
13. continue to the next item.

## Definition of “implemented”

A feature is not implemented if it consists only of:
- empty files,
- comments,
- TODOs,
- mock cards,
- fake data with no path to real data,
- routes with placeholder text,
- uncalled service code,
- interfaces with no implementation.

Stubs are permitted only for dependencies that genuinely cannot be exercised locally, and must be clearly documented.

## Generate all necessary project files

Codex is explicitly authorized and instructed to create whatever repository files are needed, including:

- source files,
- package manifests,
- workspace files,
- environment templates,
- Dockerfiles,
- Compose manifests,
- database schemas,
- migrations,
- seed scripts,
- contracts,
- protobuf/schema files,
- API definitions,
- frontend components,
- styles,
- services,
- workers,
- CLI clients,
- mobile/desktop clients,
- SDKs,
- tests,
- fixtures,
- benchmarks,
- infrastructure code,
- CI workflows,
- observability configuration,
- security configuration,
- policies,
- documentation,
- ADRs,
- runbooks,
- registry metadata,
- provenance metadata,
- scripts,
- tooling.

Do not wait for the user to create boilerplate files manually.

## Quality recovery

If a quality command fails:
- inspect failure,
- fix it,
- rerun,
- repeat until passing or a genuine external blocker is identified.

Do not knowingly move to the next phase leaving ordinary compilation/type/lint/test errors behind.

## Resource-aware implementation

ATLAS may include components too heavy to run simultaneously on a normal laptop.

Support profiles such as:
- core
- web
- database
- data
- ai
- streaming
- observability
- security
- full

A developer editing React should not need the entire big-data stack running.

## Long-range completion

The roadmap is expected to take many implementation cycles.

Codex must treat `CHECKPOINT.md`, `.atlas/progress.json`, the registry and roadmap as persistent memory so each run continues the same build rather than restarting architecture design.

## Final completion criteria

Do not mark ATLAS complete until:
- required product surfaces exist,
- core flows are integrated,
- major ecosystems meet parity targets,
- tests/security/observability are operational,
- infrastructure is reproducible,
- technology registry shows defined scope coverage,
- no critical placeholder-only areas remain,
- documented quality gates pass.
