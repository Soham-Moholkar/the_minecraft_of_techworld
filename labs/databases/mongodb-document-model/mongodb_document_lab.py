"""MongoDB document modeling, compound-index, and atomic-update experiments."""

from __future__ import annotations

import json
import os
import pathlib
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import WriteError
from pymongo.server_api import ServerApi

DATABASE_NAME = "atlas_document_lab"
ORDERS_COLLECTION = "atlas_orders"
INVENTORY_COLLECTION = "atlas_inventory"
EVIDENCE_NAME = "mongodb-document-evidence.json"


def assert_lab_identity(status: Mapping[str, object]) -> None:
    """Refuse destructive lifecycle work unless the dedicated lab user is active."""

    auth_info = status.get("authInfo")
    if not isinstance(auth_info, Mapping):
        raise RuntimeError("MongoDB did not report an authenticated lab identity")
    users = auth_info.get("authenticatedUsers")
    if not isinstance(users, Sequence) or isinstance(users, (str, bytes)):
        raise RuntimeError("MongoDB did not report an authenticated lab identity")
    identities = {
        (item.get("user"), item.get("db"))
        for item in users
        if isinstance(item, Mapping)
    }
    if identities != {("atlas_document_lab", DATABASE_NAME)}:
        raise RuntimeError("MongoDB lab requires the dedicated atlas_document_lab user")


def _verify_lab_connection(database: Any) -> None:
    database.command("ping")
    status = database.command({"connectionStatus": 1, "showPrivileges": False})
    if not isinstance(status, Mapping):
        raise RuntimeError("MongoDB returned an invalid connection status")
    assert_lab_identity(status)


def connect() -> MongoClient[dict[str, Any]]:
    """Create a bounded Stable API client for the fixed disposable database."""

    url = os.getenv(
        "ATLAS_MONGODB_LAB_URL",
        "mongodb://atlas_document_lab:atlas_document_lab_dev_only@"
        "localhost:57017/atlas_document_lab?authSource=atlas_document_lab",
    )
    return MongoClient(
        url,
        appname="atlas-mongodb-document-lab",
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=2000,
        connectTimeoutMS=2000,
        socketTimeoutMS=5000,
        tz_aware=True,
    )


def reset_collections() -> None:
    """Drop only the two allowlisted collections in the lab database."""

    with connect() as client:
        database = client[DATABASE_NAME]
        _verify_lab_connection(database)
        for collection_name in (ORDERS_COLLECTION, INVENTORY_COLLECTION):
            database.drop_collection(collection_name)


def reset_generated_state(state_dir: pathlib.Path) -> None:
    """Remove generated evidence while preserving unrelated learner notes."""

    for name in (EVIDENCE_NAME, "state.json"):
        target = state_dir / name
        if target.exists():
            target.unlink()
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()


def _prepare_collections() -> None:
    with connect() as client:
        database = client[DATABASE_NAME]
        _verify_lab_connection(database)
        for collection_name in (ORDERS_COLLECTION, INVENTORY_COLLECTION):
            database.drop_collection(collection_name)
        database.create_collection(
            ORDERS_COLLECTION,
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "order_id",
                        "tenant_slug",
                        "status",
                        "created_at",
                        "line_items",
                    ],
                    "properties": {
                        "order_id": {"bsonType": "string"},
                        "tenant_slug": {"bsonType": "string"},
                        "status": {"enum": ["open", "paid", "shipped"]},
                        "created_at": {"bsonType": "date"},
                        "line_items": {"bsonType": "array", "minItems": 1},
                    },
                }
            },
            validationAction="error",
        )
        database.create_collection(INVENTORY_COLLECTION)
        base = datetime(2026, 1, 1, tzinfo=UTC)
        orders = [
            {
                "order_id": f"order-{index:04d}",
                "tenant_slug": f"tenant-{index % 4}",
                "status": ("open", "paid", "shipped")[index % 3],
                "created_at": base + timedelta(minutes=index),
                # Embedding keeps the order's small, bounded line-item aggregate
                # consistent and readable without a cross-collection join.
                "line_items": [
                    {"sku": f"sku-{index % 12:02d}", "quantity": 1 + index % 3}
                ],
            }
            for index in range(1, 241)
        ]
        database[ORDERS_COLLECTION].insert_many(orders, ordered=True)
        database[INVENTORY_COLLECTION].insert_one(
            {"sku": "sku-01", "available": 10, "version": 1}
        )


def _query_ids(collection: Any) -> list[str]:
    cursor = (
        collection.find(
            {"tenant_slug": "tenant-1", "status": "open"},
            {"_id": 0, "order_id": 1},
        )
        .sort("created_at", DESCENDING)
        .limit(25)
    )
    return [str(document["order_id"]) for document in cursor]


def _explain(collection: Any) -> Mapping[str, Any]:
    raw = (
        collection.find(
            {"tenant_slug": "tenant-1", "status": "open"},
            {"_id": 0, "order_id": 1},
        )
        .sort("created_at", DESCENDING)
        .limit(25)
        .explain()
    )
    if not isinstance(raw, Mapping):
        raise RuntimeError("MongoDB returned a non-document explain plan")
    return cast(Mapping[str, Any], raw)


def plan_stages(value: object) -> list[dict[str, object]]:
    """Extract stage/index structure without query predicates or document values."""

    stages: list[dict[str, object]] = []
    if isinstance(value, Mapping):
        stage = value.get("stage")
        if isinstance(stage, str):
            record: dict[str, object] = {"stage": stage}
            index_name = value.get("indexName")
            if isinstance(index_name, str):
                record["index_name"] = index_name
            stages.append(record)
        for key, child in value.items():
            if key not in {"parsedQuery", "command", "filter"}:
                stages.extend(plan_stages(child))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            stages.extend(plan_stages(child))
    return stages


def _index_experiment() -> dict[str, object]:
    with connect() as client:
        collection = client[DATABASE_NAME][ORDERS_COLLECTION]
        before_ids = _query_ids(collection)
        before_stages = plan_stages(_explain(collection))
        collection.create_index(
            [("tenant_slug", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
            name="ix_tenant_status_created",
        )
        after_ids = _query_ids(collection)
        after_stages = plan_stages(_explain(collection))
    return {
        "results_equal": before_ids == after_ids,
        "result_count": len(after_ids),
        "before_stages": before_stages,
        "after_stages": after_stages,
        "before_collection_scan": any(item["stage"] == "COLLSCAN" for item in before_stages),
        "selected_compound_index": any(
            item.get("stage") == "IXSCAN"
            and item.get("index_name") == "ix_tenant_status_created"
            for item in after_stages
        ),
    }


def _validation_experiment() -> dict[str, object]:
    error_code: int | None = None
    with connect() as client:
        try:
            client[DATABASE_NAME][ORDERS_COLLECTION].insert_one(
                {"order_id": "invalid-order", "status": "open"}
            )
        except WriteError as error:
            error_code = error.code
    return {
        "invalid_document_rejected": error_code == 121,
        "error_code": error_code,
        "expected_validation_code": 121,
    }


def _optimistic_update_experiment() -> dict[str, object]:
    with connect() as client:
        inventory = client[DATABASE_NAME][INVENTORY_COLLECTION]
        first = inventory.update_one(
            {"sku": "sku-01", "version": 1},
            {"$inc": {"available": -2, "version": 1}},
        )
        stale = inventory.update_one(
            {"sku": "sku-01", "version": 1},
            {"$inc": {"available": -1, "version": 1}},
        )
        fresh = inventory.find_one({"sku": "sku-01"})
        if fresh is None:
            raise RuntimeError("inventory document disappeared")
        retry = inventory.update_one(
            {"sku": "sku-01", "version": fresh["version"]},
            {"$inc": {"available": -1, "version": 1}},
        )
        final = inventory.find_one({"sku": "sku-01"})
        if final is None:
            raise RuntimeError("inventory document disappeared")
    return {
        "first_update_applied": first.modified_count == 1,
        "stale_update_rejected": stale.modified_count == 0,
        "fresh_retry_applied": retry.modified_count == 1,
        "final_available": int(final["available"]),
        "final_version": int(final["version"]),
    }


def prepare_lab(state_dir: pathlib.Path) -> pathlib.Path:
    """Run all experiments and store sanitized structural evidence."""

    _prepare_collections()
    evidence = {
        "engine": "mongodb",
        "generated_at": datetime.now(UTC).isoformat(),
        "document_model": {
            "orders_embed_line_items": True,
            "reason": "bounded line items share the order lifecycle and atomicity boundary",
        },
        "index": _index_experiment(),
        "validation": _validation_experiment(),
        "optimistic_update": _optimistic_update_experiment(),
    }
    state_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = state_dir / EVIDENCE_NAME
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (state_dir / "state.json").write_text(
        json.dumps({"status": "ready", "evidence": EVIDENCE_NAME}, indent=2),
        encoding="utf-8",
    )
    return evidence_path
