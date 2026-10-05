"""MongoDB-backed, tenant-scoped project document projection.

PostgreSQL remains authoritative. MongoDB is useful here because the projection
embeds read-oriented project summary data in one document. Publication uses a new
generation and changes a small state pointer only after all new documents exist;
readers therefore see the old complete generation or the new complete generation,
never a partially refreshed mixture, without requiring cross-store transactions.
"""

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pymongo import MongoClient, ReplaceOne
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_api.models import Note, Organization, Project
from atlas_api.schemas import (
    DocumentProjectionItem,
    DocumentProjectionPublishRead,
    DocumentProjectionSnapshotRead,
)

MongoDocument = dict[str, Any]
MongoClientFactory = Callable[[str], MongoClient[MongoDocument]]
DATABASE_NAME = "atlas_document"
SNAPSHOTS_COLLECTION = "project_snapshots"
STATE_COLLECTION = "projection_state"


class DocumentProjectionUnavailable(RuntimeError):
    """Raised when an explicit publication cannot reach the optional provider."""


def _default_client(url: str) -> MongoClient[MongoDocument]:
    """Create a short-lived Stable API client with bounded failure latency."""

    return MongoClient(
        url,
        appname="atlas-document-projection",
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=2000,
        connectTimeoutMS=2000,
        socketTimeoutMS=3000,
        tz_aware=True,
    )


def normalize_projection_documents(
    documents: Sequence[Mapping[str, object]],
) -> list[DocumentProjectionItem]:
    """Validate the allowlisted public subset and discard every other BSON field."""

    items: list[DocumentProjectionItem] = []
    for document in documents:
        project_slug = document.get("project_slug")
        status = document.get("status")
        note_count = document.get("note_count")
        created_at = document.get("created_at")
        if not isinstance(project_slug, str) or not isinstance(status, str):
            raise ValueError("MongoDB returned invalid project text fields")
        if isinstance(note_count, bool) or not isinstance(note_count, int):
            raise ValueError("MongoDB returned an invalid note count")
        if not isinstance(created_at, datetime):
            raise ValueError("MongoDB returned an invalid project timestamp")
        items.append(
            DocumentProjectionItem(
                project_slug=project_slug,
                status=status,
                note_count=note_count,
                created_at=created_at,
            )
        )
    return items


class MongoProjectProjectionRepository:
    """Publish and read a derived MongoDB projection for one authenticated tenant."""

    def __init__(
        self,
        session: Session,
        mongodb_url: str | None,
        *,
        client_factory: MongoClientFactory = _default_client,
    ) -> None:
        self.session = session
        self.mongodb_url = mongodb_url
        self.client_factory = client_factory

    @staticmethod
    def _unavailable() -> DocumentProjectionSnapshotRead:
        return DocumentProjectionSnapshotRead(
            status="unavailable",
            document_count=0,
            items=[],
            index_strategy=(
                "organization_slug + generation + created_at compound tenant index"
            ),
            consistency_model="PostgreSQL authoritative; generation-switched MongoDB read model.",
            notes=["Start the optional MongoDB profile to publish and inspect documents."],
            generated_at=datetime.now(UTC),
        )

    def read(self, *, organization_slug: str) -> DocumentProjectionSnapshotRead:
        """Read only the generation published for the authenticated tenant."""

        if self.mongodb_url is None:
            return self._unavailable()
        try:
            with self.client_factory(self.mongodb_url) as client:
                database = client[DATABASE_NAME]
                database.command("ping")
                state = database[STATE_COLLECTION].find_one(
                    {"organization_slug": organization_slug},
                    {"_id": 0, "generation": 1, "published_at": 1},
                )
                if state is None:
                    documents: list[MongoDocument] = []
                    published_at = None
                else:
                    generation = state.get("generation")
                    if not isinstance(generation, str) or len(generation) != 32:
                        raise ValueError("MongoDB returned an invalid projection generation")
                    published_at = state.get("published_at")
                    documents = list(
                        database[SNAPSHOTS_COLLECTION]
                        .find(
                            {
                                "organization_slug": organization_slug,
                                "generation": generation,
                            },
                            {
                                "_id": 0,
                                "project_slug": 1,
                                "status": 1,
                                "note_count": 1,
                                "created_at": 1,
                            },
                        )
                        .sort("created_at", -1)
                        .limit(25)
                    )
                items = normalize_projection_documents(documents)
                count = (
                    database[SNAPSHOTS_COLLECTION].count_documents(
                        {
                            "organization_slug": organization_slug,
                            "generation": state["generation"],
                        }
                    )
                    if state is not None
                    else 0
                )
            return DocumentProjectionSnapshotRead(
                status="available" if state is not None else "empty",
                document_count=count,
                published_at=published_at,
                items=items,
                index_strategy=(
                    "organization_slug + generation + created_at compound tenant index"
                ),
                consistency_model=(
                    "PostgreSQL authoritative; complete MongoDB generations switch atomically."
                ),
                notes=[
                    "Projection refresh is explicit and eventually consistent with PostgreSQL.",
                    "Descriptions, note bodies, actors, and tenant identifiers are not returned.",
                ],
                generated_at=datetime.now(UTC),
            )
        except (PyMongoError, ValueError, TypeError, KeyError):
            # Driver errors can contain hosts, users, or topology details. The
            # ordinary tenant API deliberately returns one generic provider state.
            return self._unavailable()

    def publish(self, *, organization_slug: str) -> DocumentProjectionPublishRead:
        """Materialize one complete generation from an authorized relational query."""

        if self.mongodb_url is None:
            raise DocumentProjectionUnavailable("document projection unavailable")

        rows = self.session.execute(
            select(Project, func.count(Note.id))
            .join(Organization)
            .outerjoin(Note)
            .where(Organization.slug == organization_slug)
            .group_by(Project.id)
            .order_by(Project.created_at.desc())
        ).all()
        generation = uuid4().hex
        published_at = datetime.now(UTC)
        operations: list[ReplaceOne[MongoDocument]] = []
        for project, note_count in rows:
            document: MongoDocument = {
                "organization_slug": organization_slug,
                "generation": generation,
                "project_id": str(project.id),
                "project_slug": project.slug,
                "name": project.name,
                "status": project.status,
                "note_count": int(note_count),
                "created_at": project.created_at,
                "published_at": published_at,
            }
            operations.append(
                ReplaceOne(
                    {
                        "organization_slug": organization_slug,
                        "generation": generation,
                        "project_id": str(project.id),
                    },
                    document,
                    upsert=True,
                )
            )

        try:
            with self.client_factory(self.mongodb_url) as client:
                database = client[DATABASE_NAME]
                database.command("ping")
                snapshots = database[SNAPSHOTS_COLLECTION]
                if operations:
                    snapshots.bulk_write(operations, ordered=True)
                # This state document is one MongoDB atomic write. Readers do not
                # select the new generation until every replacement above succeeds.
                database[STATE_COLLECTION].replace_one(
                    {"organization_slug": organization_slug},
                    {
                        "organization_slug": organization_slug,
                        "generation": generation,
                        "published_at": published_at,
                        "document_count": len(operations),
                    },
                    upsert=True,
                )
                # Do not delete other generations during publication. Another
                # publisher may be building one, and a reader may still hold an
                # older pointer. Both would lose data under a $ne cleanup. Retain
                # immutable generations until a coordinated offline retention
                # job can prove that no publisher/reader still needs them.
                removed = 0
        except (PyMongoError, ValueError, TypeError) as error:
            raise DocumentProjectionUnavailable("document projection unavailable") from error

        return DocumentProjectionPublishRead(
            published_count=len(operations),
            removed_count=removed,
            published_at=published_at,
        )
