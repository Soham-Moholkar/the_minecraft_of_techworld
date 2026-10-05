# Current Technology Notes — 24 August 2026

These notes are context, not permanent version pins. Codex must re-check official documentation before a future dependency installation or major upgrade.

## shadcn/ui

The current official shadcn documentation describes shadcn/ui as open code and a code distribution system rather than a conventional opaque component library.

Current official docs also show:
- Base UI is the default primitive choice for new shadcn projects as of July 2026.
- Radix remains supported.
- shadcn now documents composition structures specifically to make component composition more reliable for humans and coding agents.
- the component catalog includes newer chat-oriented primitives such as Message, Message Scroller, Bubble, Attachment and Marker.
- shadcn provides a registry model and CLI for adding components.
- shadcn explicitly points to community registry components when a needed component is not in the built-in set.

Official references:
- https://ui.shadcn.com/docs
- https://ui.shadcn.com/docs/components
- https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default
- https://ui.shadcn.com/docs/changelog/2026-06-chat-components
- https://ui.shadcn.com/docs/changelog/2026-04-component-composition
- https://ui.shadcn.com/docs/cli

### ATLAS consequence

Use shadcn source-owned components heavily. Create a large ATLAS-specific composition layer rather than adding unrelated UI libraries for every widget.

For community components:
- inspect source,
- confirm license,
- review accessibility,
- review dependencies,
- normalize styling,
- add tests.

## TanStack

Use current official TanStack documentation when adopting Query/Table/Router tooling. The ATLAS recommendation is:
- TanStack Query for server-state concerns,
- TanStack Table for large data-heavy tables.

Official reference:
- https://tanstack.com/

## Apache ecosystem

The Apache ecosystem is central to ATLAS's data engineering track.

Official Apache sources confirm:
- Spark is a unified engine for large-scale analytics and supports batch/streaming, SQL and data-science/ML workflows.
- Kafka is a distributed event-streaming platform.
- Flink is a distributed engine for stateful bounded/unbounded stream computation.

At the date of this file, official pages list modern 2026 releases such as Spark 4.x, Kafka 4.x and Flink 2.x. Do not hard-pin ATLAS to these values without re-checking.

Official references:
- https://spark.apache.org/
- https://kafka.apache.org/
- https://flink.apache.org/
- https://airflow.apache.org/
- https://iceberg.apache.org/
- https://arrow.apache.org/
- https://superset.apache.org/
- https://apache.org/

## Versioning rule

Record runtime versions in:
- lockfiles,
- container tags,
- environment manifests,
- lab metadata.

Content should explain concepts in a version-aware way.
If syntax is version-specific, display the tested version.

## Online resources

Codex may consult official docs and reputable source repositories while implementing.

Order of preference:
1. official framework/project docs,
2. official repositories/examples,
3. standards/specifications,
4. trusted maintainers,
5. community examples.

Do not copy large undocumented snippets from random sites.
