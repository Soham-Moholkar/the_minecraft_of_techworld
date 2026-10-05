"""SQLAlchemy session boundary and provider-neutral engine configuration."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from atlas_api.config import get_settings


class Base(DeclarativeBase):
    """Declarative metadata root imported by migrations."""


def _create_engine():  # type: ignore[no-untyped-def]
    url = get_settings().database_url
    # SQLite is the L0/L1 local adapter. PostgreSQL is the Compose/production path.
    # check_same_thread is SQLite-specific and allows FastAPI's worker-thread handoff.
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session]:
    """Yield one transaction-capable session per request and always close it."""

    with SessionLocal() as session:
        yield session
