"""Source-reviewed, tenant-safe query workbench operations."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_api.models import Note, Organization, Project
from atlas_api.schemas import (
    DatabaseWorkbenchItem,
    DatabaseWorkbenchRead,
    DatabaseWorkbenchRequest,
)


class DatabaseWorkbenchRepository:
    """Execute named read templates instead of accepting arbitrary SQL."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def execute(
        self,
        request: DatabaseWorkbenchRequest,
        *,
        organization_slug: str,
    ) -> DatabaseWorkbenchRead:
        # The branch is deliberately explicit so every future query name must be
        # reviewed, parameterized, tenant-scoped, bounded, and separately tested.
        if request.query_name == "tenant_projects_by_status":
            rows = self.session.execute(
                select(Project.slug, Project.status, func.count(Note.id), Project.created_at)
                .join(Organization)
                .outerjoin(Note)
                .where(
                    Organization.slug == organization_slug,
                    Project.status == request.status,
                )
                .group_by(Project.id)
                .order_by(Project.created_at.desc())
                .limit(request.limit)
            ).all()
        items = [
            DatabaseWorkbenchItem(
                project_slug=str(slug),
                status=str(status),
                note_count=int(note_count),
                created_at=created_at,
            )
            for slug, status, note_count, created_at in rows
        ]
        engine = self.session.get_bind().dialect.name
        return DatabaseWorkbenchRead(
            engine="postgresql" if engine == "postgresql" else "sqlite",
            query_name=request.query_name,
            parameters=request,
            items=items,
            returned_count=len(items),
            safety_model=(
                "Named template + typed parameters + authenticated tenant predicate "
                "+ 25-row ceiling."
            ),
            generated_at=datetime.now(UTC),
        )
