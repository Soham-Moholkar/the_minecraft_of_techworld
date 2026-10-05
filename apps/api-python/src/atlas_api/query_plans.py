"""Read-only, tenant-safe query-plan providers for the Data Estate surface.

This module deliberately does not accept SQL from an HTTP caller. Query plans can
expose schema details and some engines offer statement forms with side effects, so
ATLAS maps a small public query name to SQL owned and reviewed by the application.
"""

import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, Literal, cast

from sqlalchemy import text
from sqlalchemy.orm import Session

from atlas_api.schemas import (
    QueryPlanNode,
    QueryPlanParameters,
    QueryPlanRead,
)

QueryName = Literal["tenant_projects_by_status"]
ProjectStatus = Literal["active", "paused", "archived"]

# The query is fixed in source and both caller-controlled values are bound
# parameters. Besides preventing injection, the tenant predicate makes the
# authorization boundary visible in the same SQL whose plan is inspected.
TENANT_PROJECTS_BY_STATUS_SQL = """
SELECT p.id, p.slug, p.name, p.status
FROM projects AS p
JOIN organizations AS o ON o.id = p.organization_id
WHERE o.slug = :organization_slug AND p.status = :status
ORDER BY p.created_at DESC
LIMIT 25
""".strip()

_SQLITE_RELATION = re.compile(r"^(?:SCAN|SEARCH)\s+(\S+)")
_RELATION_ALIASES = {"p": "projects", "o": "organizations"}


class UnsupportedQueryPlanDialect(RuntimeError):
    """Raised when no reviewed EXPLAIN adapter exists for the active engine."""


def _optional_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _postgres_detail(plan: Mapping[str, Any]) -> str:
    """Describe plan shape without echoing predicates or tenant literals.

    PostgreSQL JSON can include resolved filter values. Returning only structural
    fields keeps the diagnostic useful while avoiding unnecessary data reflection.
    """

    operation = str(plan.get("Node Type", "Unknown"))
    parts = [operation]
    relation = plan.get("Relation Name")
    if isinstance(relation, str):
        parts.append(f"on {relation}")
    index = plan.get("Index Name")
    if isinstance(index, str):
        parts.append(f"using {index}")
    join_type = plan.get("Join Type")
    if isinstance(join_type, str):
        parts.append(f"({join_type.lower()} join)")
    return " ".join(parts)


def normalise_postgresql_plan(root: Mapping[str, Any]) -> list[QueryPlanNode]:
    """Flatten PostgreSQL's recursive JSON plan into portable preorder nodes."""

    nodes: list[QueryPlanNode] = []

    def visit(plan: Mapping[str, Any]) -> None:
        relation_value = plan.get("Relation Name")
        nodes.append(
            QueryPlanNode(
                operation=str(plan.get("Node Type", "Unknown")),
                relation=relation_value if isinstance(relation_value, str) else None,
                detail=_postgres_detail(plan),
                estimated_rows=_optional_float(plan.get("Plan Rows")),
                estimated_cost=_optional_float(plan.get("Total Cost")),
            )
        )
        children = plan.get("Plans", [])
        if not isinstance(children, Sequence) or isinstance(children, (str, bytes)):
            return
        for child in children:
            if isinstance(child, Mapping):
                visit(cast(Mapping[str, Any], child))

    visit(root)
    return nodes


def normalise_sqlite_plan(rows: Sequence[Sequence[object]]) -> list[QueryPlanNode]:
    """Convert SQLite's flat EXPLAIN QUERY PLAN rows into the shared contract."""

    nodes: list[QueryPlanNode] = []
    for row in rows:
        detail = str(row[3]) if len(row) > 3 else "Unknown"
        operation = detail.split(maxsplit=1)[0].title() if detail else "Unknown"
        relation_match = _SQLITE_RELATION.match(detail)
        relation = relation_match.group(1) if relation_match else None
        if relation is not None:
            relation = _RELATION_ALIASES.get(relation, relation)
        nodes.append(
            QueryPlanNode(
                operation=operation,
                relation=relation,
                detail=detail,
            )
        )
    return nodes


def normalise_mariadb_plan(root: Mapping[str, Any]) -> list[QueryPlanNode]:
    """Extract portable structure from MariaDB's recursive JSON plan.

    MariaDB can include resolved predicates in ``attached_condition``. This
    traversal only emits structural container names and reviewed table fields, so
    bound tenant values can never be reflected by the diagnostic endpoint.
    """

    nodes: list[QueryPlanNode] = []

    def visit(value: object, container: str | None = None) -> None:
        if isinstance(value, Mapping):
            table = value.get("table")
            if isinstance(table, Mapping):
                table_name = table.get("table_name")
                access_type = table.get("access_type")
                key = table.get("key")
                relation = table_name if isinstance(table_name, str) else None
                if relation is not None:
                    relation = _RELATION_ALIASES.get(relation, relation)
                operation = (
                    f"{str(access_type).replace('_', ' ').title()} access"
                    if isinstance(access_type, str)
                    else "Table access"
                )
                detail_parts = [operation]
                if relation:
                    detail_parts.append(f"on {relation}")
                if isinstance(key, str):
                    detail_parts.append(f"using {key}")
                nodes.append(
                    QueryPlanNode(
                        operation=operation,
                        relation=relation,
                        detail=" ".join(detail_parts),
                        estimated_rows=_optional_float(table.get("rows")),
                    )
                )
            elif container in {"filesort", "temporary_table"}:
                label = container.replace("_", " ").title()
                nodes.append(QueryPlanNode(operation=label, detail=label))

            for key_name, child in value.items():
                # The table mapping has already been reduced to allowlisted fields.
                if key_name == "table":
                    continue
                visit(child, str(key_name))
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for child in value:
                visit(child, container)

    visit(root)
    if not nodes:
        raise ValueError("MariaDB returned a query plan without structural nodes")
    return nodes


def _mariadb_root(raw: object) -> Mapping[str, Any]:
    """Validate MariaDB's JSON EXPLAIN document before traversal."""

    value = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(value, Mapping):
        raise ValueError("MariaDB returned an invalid query plan")
    return cast(Mapping[str, Any], value)


def _postgres_root(raw: object) -> Mapping[str, Any]:
    """Validate the small portion of PostgreSQL's driver-dependent JSON shape."""

    value = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise ValueError("PostgreSQL returned an invalid query plan")
    first = value[0]
    if not isinstance(first, Mapping):
        raise ValueError("PostgreSQL returned an invalid query plan")
    plan = first.get("Plan")
    if not isinstance(plan, Mapping):
        raise ValueError("PostgreSQL returned an invalid query plan")
    return cast(Mapping[str, Any], plan)


def _recommendations(nodes: Sequence[QueryPlanNode]) -> list[str]:
    """Offer bounded guidance without claiming a synthetic plan is universally best."""

    operations = " ".join(node.operation.lower() for node in nodes)
    details = " ".join(node.detail.lower() for node in nodes)
    if "seq scan" in operations or "scan p" in details:
        return [
            "Review a composite projects(status, created_at) index against representative data.",
            "Measure write cost and production-like selectivity before retaining any new index.",
        ]
    if "index" in operations or "using index" in details:
        return [
            "The planner selected an index-backed path; validate latency with representative data.",
        ]
    return ["Compare this estimated plan with representative data before changing indexes."]


class QueryPlanRepository:
    """Execute reviewed planning statements through the request-scoped session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def explain_tenant_projects_by_status(
        self, *, organization_slug: str, status: ProjectStatus
    ) -> QueryPlanRead:
        """Plan the fixed tenant project lookup without executing the underlying SELECT."""

        bind = self.session.get_bind()
        dialect = bind.dialect.name
        parameters = {"organization_slug": organization_slug, "status": status}

        if dialect == "postgresql":
            # EXPLAIN without ANALYZE asks the optimizer for estimates only. ANALYZE
            # is intentionally absent because it would execute the underlying query.
            raw = self.session.execute(
                text(f"EXPLAIN (FORMAT JSON) {TENANT_PROJECTS_BY_STATUS_SQL}"), parameters
            ).scalar_one()
            nodes = normalise_postgresql_plan(_postgres_root(raw))
            engine: Literal["postgresql", "sqlite", "mariadb"] = "postgresql"
        elif dialect == "sqlite":
            result = self.session.execute(
                text(f"EXPLAIN QUERY PLAN {TENANT_PROJECTS_BY_STATUS_SQL}"), parameters
            )
            rows = [tuple(row) for row in result]
            nodes = normalise_sqlite_plan(rows)
            engine = "sqlite"
        elif dialect == "mariadb":
            # MariaDB JSON planning is estimate-only and executes no product rows.
            # The source-owned statement and bound values retain the same tenant
            # and injection boundaries as the PostgreSQL/SQLite adapters.
            raw = self.session.execute(
                text(f"EXPLAIN FORMAT=JSON {TENANT_PROJECTS_BY_STATUS_SQL}"), parameters
            ).scalar_one()
            nodes = normalise_mariadb_plan(_mariadb_root(raw))
            engine = "mariadb"
        else:
            raise UnsupportedQueryPlanDialect(
                f"query planning is not configured for database dialect {dialect!r}"
            )

        return QueryPlanRead(
            engine=engine,
            query_name="tenant_projects_by_status",
            # The public response describes the caller-controlled diagnostic input,
            # but does not duplicate the authenticated tenant identifier.
            parameters=QueryPlanParameters(status=status),
            nodes=nodes,
            recommendations=_recommendations(nodes),
            generated_at=datetime.now(UTC),
        )
