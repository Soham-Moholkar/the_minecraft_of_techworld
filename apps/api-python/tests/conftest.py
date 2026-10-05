"""Isolated in-memory database fixtures for API tests."""

import os

os.environ["ATLAS_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["ATLAS_DEV_TOKEN"] = "atlas-test-token-is-long-enough"  # noqa: S105

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from atlas_api.database import Base, get_session
from atlas_api.main import app
from atlas_api.models import Organization


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with testing_session.begin() as session:
        session.add_all(
            [
                Organization(slug="northstar", name="Northstar Systems"),
                Organization(slug="other-tenant", name="Other Tenant"),
            ]
        )

    def override_session():  # type: ignore[no-untyped-def]
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer atlas-test-token-is-long-enough"}
