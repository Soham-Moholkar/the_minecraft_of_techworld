# 18 — Open-Source Sourcing, Reuse and Provenance Policy

## Purpose

ATLAS should benefit aggressively from the existing open-source ecosystem without becoming a stitched-together Frankenstein repository.

Codex is encouraged to use the internet and public source repositories when available, but all reuse must preserve ATLAS architecture, licensing clarity, security and maintainability.

## Sourcing hierarchy

When implementing a technology or integration, prefer sources in this order:

1. official specification or standard,
2. official framework/project documentation,
3. official framework/project repository,
4. official examples/starters/generators,
5. well-maintained reference implementations,
6. reputable open-source projects,
7. community examples only when the above are insufficient.

## Default integration rule

Prefer, in order:

1. install/use the maintained library as a dependency,
2. generate from the framework's official scaffolding/tooling,
3. integrate an external system through an adapter/API/plugin boundary,
4. adapt a small auditable utility/component,
5. copy source only when there is a strong architectural reason and the license explicitly permits it.

Do not copy an entire repository into ATLAS merely because it already implements something similar.

## What Codex may reuse

Good candidates:
- shadcn source components,
- official framework starters,
- small utilities,
- protocol examples,
- Docker/Kubernetes reference configurations,
- official SDK examples,
- schema definitions,
- permissively licensed UI patterns,
- benchmark harness concepts,
- test patterns,
- generated clients,
- maintained libraries.

## What Codex should not do

Do not:
- blindly concatenate repositories,
- import unknown code without license review,
- copy random blog snippets into production paths,
- mix incompatible architecture styles without adapters,
- duplicate libraries already present,
- hide copied code provenance,
- add abandoned dependencies without an explicit legacy reason,
- import telemetry/tracking unexpectedly,
- bring secrets, credentials or environment-specific configuration from public examples,
- copy vulnerable demo code into production paths.

## Provenance records

Create:

```text
provenance/
├── external-components.yaml
├── imported-code.yaml
├── generated-clients.yaml
└── licenses/
```

For adapted/copied source, record:

```yaml
id: shadcn-data-table-adaptation
source:
  project: shadcn/ui
  url: https://...
  commit_or_version: ...
license: MIT
retrieved_at: YYYY-MM-DD

used_in:
  - packages/ui/src/data-grid/...

reuse_type: adapted_source

changes:
  - integrated ATLAS design tokens
  - added virtualization
  - added accessibility tests

review:
  security: passed
  dependencies: passed
  accessibility: passed
```

Dependencies installed normally through package managers do not each require a copied-source record, but the technology registry must still track significant dependencies.

## License policy

Before copying/adapting source:
- identify license,
- verify compatibility,
- preserve notices/attribution when required,
- do not copy code with unclear licensing.

Create an automated dependency/license inventory where practical.

## Security review for external code

Before adoption inspect:
- transitive dependencies,
- install scripts,
- network calls,
- telemetry,
- filesystem access,
- credential handling,
- unsafe deserialization,
- code execution,
- known vulnerabilities,
- package maintenance/activity.

## UI-specific rule

For online UI components:
- prefer shadcn/ui and owned source,
- inspect community registry source,
- normalize design tokens,
- remove unwanted tracking,
- verify keyboard/screen-reader behavior,
- add interaction tests.

## Architecture preservation

External code must conform to ATLAS boundaries.

Bad:

```text
ATLAS service
  directly depends on three unrelated vendor-specific APIs everywhere
```

Good:

```text
ATLAS interface
      |
      +-- Provider A adapter
      +-- Provider B adapter
      +-- Provider C adapter
```

## “Use existing code” strategy

Codex should absolutely study strong public implementations to accelerate work.

The desired behavior is:

```text
study existing engineering
        +
use official libraries
        +
reuse audited pieces
        +
generate ATLAS-owned integration
        +
test/security/telemetry
        =
cohesive ATLAS implementation
```

not:

```text
repo A + repo B + repo C copied together
```

## Version pinning

Pin meaningful runtime/dependency versions through:
- lockfiles,
- container tags,
- build manifests,
- technology registry.

Avoid unbounded `latest` tags for reproducible infrastructure.

## Dependency replacement

Provider interfaces should make it possible to replace important technologies later without rewriting the full product.

This is a deliberate ATLAS learning mechanism.
