"""Deterministic, idempotent seed data for a useful first-run product."""

from sqlalchemy import select

from atlas_api.database import Base, SessionLocal, engine
from atlas_api.models import Organization, Project


def seed() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as session:
        organization = session.scalar(select(Organization).where(Organization.slug == "northstar"))
        if organization is None:
            organization = Organization(slug="northstar", name="Northstar Systems")
            session.add(organization)
            session.flush()
        examples = (
            (
                "financial-intelligence",
                "Financial Intelligence",
                "Live risk and portfolio analytics.",
            ),
            ("knowledge-foundry", "Knowledge Foundry", "Permission-aware RAG and agent workflows."),
            ("telemetry-grid", "Telemetry Grid", "Streaming service health and incident signals."),
        )
        # Slugs are unique within a tenant, not globally. Check each example so a
        # partially seeded checkout recovers without changing operator edits.
        for slug, name, description in examples:
            existing = session.scalar(
                select(Project.id).where(
                    Project.organization_id == organization.id,
                    Project.slug == slug,
                )
            )
            if existing is None:
                session.add(
                    Project(
                        organization_id=organization.id,
                        slug=slug,
                        name=name,
                        description=description,
                    )
                )


if __name__ == "__main__":
    seed()
