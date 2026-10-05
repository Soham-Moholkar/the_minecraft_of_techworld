"""Seed recovers partial tenant state without overwriting user-owned records."""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from atlas_api import seed as module
from atlas_api.database import Base
from atlas_api.models import Organization, Project


def test_seed_is_tenant_scoped_and_recovers_partial_state(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine("sqlite:///:memory:")
    sessions = sessionmaker(bind=engine)
    monkeypatch.setattr(module, "engine", engine)
    monkeypatch.setattr(module, "SessionLocal", sessions)
    Base.metadata.create_all(engine)
    with sessions.begin() as session:
        owner = Organization(slug="northstar", name="Edited organization")
        outsider = Organization(slug="other", name="Other tenant")
        session.add_all([owner, outsider])
        session.flush()
        session.add_all(
            [
                Project(
                    organization_id=owner.id,
                    slug="knowledge-foundry",
                    name="Operator title",
                    description="Keep this edit",
                ),
                Project(
                    organization_id=outsider.id,
                    slug="financial-intelligence",
                    name="Other title",
                    description="Other content",
                ),
            ]
        )
    module.seed()
    module.seed()
    with sessions() as session:
        all_projects = session.scalars(select(Project)).all()
        assert len(all_projects) == 4
        owner = session.scalar(select(Organization).where(Organization.slug == "northstar"))
        assert owner and owner.name == "Edited organization"
        projects = {
            project.slug: project for project in all_projects if project.organization_id == owner.id
        }
        assert set(projects) == {"financial-intelligence", "knowledge-foundry", "telemetry-grid"}
        assert projects["knowledge-foundry"].description == "Keep this edit"
        assert projects["knowledge-foundry"].name == "Operator title"
    engine.dispose()
