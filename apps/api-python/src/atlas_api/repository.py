"""Repository operations keep SQLAlchemy out of HTTP route handlers."""

from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from atlas_api.models import AuditEvent, Note, Organization, Project
from atlas_api.schemas import NoteCreate, ProjectCreate


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_projects(
        self, *, organization_slug: str, limit: int, offset: int
    ) -> tuple[list[Project], int]:
        tenant_filter = Organization.slug == organization_slug
        items = list(
            self.session.scalars(
                select(Project)
                .join(Organization)
                .where(tenant_filter)
                .order_by(Project.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        total = (
            self.session.scalar(
                select(func.count()).select_from(Project).join(Organization).where(tenant_filter)
            )
            or 0
        )
        return items, total

    def get(self, project_id: UUID, *, organization_slug: str) -> Project | None:
        return self.session.scalar(
            select(Project)
            .join(Organization)
            .where(Project.id == project_id, Organization.slug == organization_slug)
        )

    def search(self, query: str, *, organization_slug: str, limit: int) -> list[Project]:
        """Search the first indexed product entity with a bounded result set.

        PostgreSQL can later replace this portable LIKE query with a weighted FTS
        adapter without changing the HTTP contract or search workspace.
        """

        pattern = f"%{query}%"
        return list(
            self.session.scalars(
                select(Project)
                .join(Organization)
                .where(
                    Organization.slug == organization_slug,
                    or_(Project.name.ilike(pattern), Project.description.ilike(pattern)),
                )
                .order_by(Project.name)
                .limit(limit)
            )
        )

    def create(self, data: ProjectCreate, *, organization_slug: str, actor: str) -> Project:
        organization = self.session.scalar(
            select(Organization).where(
                Organization.id == data.organization_id, Organization.slug == organization_slug
            )
        )
        if organization is None:
            raise LookupError("organization not found")
        if self.session.scalar(
            select(Project).where(
                Project.organization_id == organization.id, Project.slug == data.slug
            )
        ):
            raise ValueError("project slug already exists in organization")
        project = Project(**data.model_dump())
        self.session.add(project)
        self.session.flush()
        # Domain change and audit evidence share one transaction: a crash cannot
        # persist the mutation without its security record (or the inverse).
        self.session.add(
            AuditEvent(
                organization_id=organization.id,
                actor=actor,
                action="project.created",
                target_type="project",
                target_id=str(project.id),
                details={"slug": project.slug, "name": project.name},
            )
        )
        self.session.commit()
        self.session.refresh(project)
        return project

    def add_note(self, project: Project, data: NoteCreate, *, actor: str) -> Note:
        note = Note(project_id=project.id, **data.model_dump())
        self.session.add(note)
        self.session.flush()
        self.session.add(
            AuditEvent(
                organization_id=project.organization_id,
                actor=actor,
                action="project.note_added",
                target_type="note",
                target_id=str(note.id),
                details={"project_id": str(project.id)},
            )
        )
        self.session.commit()
        self.session.refresh(note)
        return note

    def list_notes(self, project: Project) -> list[Note]:
        return list(
            self.session.scalars(
                select(Note).where(Note.project_id == project.id).order_by(Note.created_at.desc())
            )
        )

    def list_audit(self, *, organization_slug: str, limit: int) -> list[AuditEvent]:
        return list(
            self.session.scalars(
                select(AuditEvent)
                .join(Organization, AuditEvent.organization_id == Organization.id)
                .where(Organization.slug == organization_slug)
                .order_by(AuditEvent.created_at.desc())
                .limit(limit)
            )
        )

    def list_audit_after(
        self, *, organization_slug: str, cursor_id: UUID, limit: int
    ) -> list[AuditEvent] | None:
        """Return tenant events strictly after a known SSE cursor.

        Returning ``None`` deliberately treats a missing cursor and a cursor owned
        by another tenant identically, so reconnect behavior cannot leak tenancy.
        """

        cursor = self.session.scalar(
            select(AuditEvent)
            .join(Organization, AuditEvent.organization_id == Organization.id)
            .where(AuditEvent.id == cursor_id, Organization.slug == organization_slug)
        )
        if cursor is None:
            return None
        return list(
            self.session.scalars(
                select(AuditEvent)
                .join(Organization, AuditEvent.organization_id == Organization.id)
                .where(
                    Organization.slug == organization_slug,
                    or_(
                        AuditEvent.created_at > cursor.created_at,
                        and_(
                            AuditEvent.created_at == cursor.created_at,
                            AuditEvent.id > cursor.id,
                        ),
                    ),
                )
                .order_by(AuditEvent.created_at, AuditEvent.id)
                .limit(limit)
            )
        )
