"""Security and protocol regression tests for the bidirectional realtime boundary."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

ALLOWED_ORIGIN = "http://localhost:3000"


def issue_ticket(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post("/v1/realtime/tickets", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    payload = response.json()
    assert payload["expires_in_seconds"] == 30
    return str(payload["ticket"])


def test_ticket_requires_http_authentication(client: TestClient) -> None:
    response = client.post("/v1/realtime/tickets")
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid credentials"}


def test_presence_round_trip_and_ticket_replay_protection(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    ticket = issue_ticket(client, auth_headers)
    request_id = str(uuid4())
    with client.websocket_connect(
        f"/v1/realtime/ws?ticket={ticket}",
        headers={"origin": ALLOWED_ORIGIN},
    ) as socket:
        socket.send_json({"type": "unknown", "request_id": request_id})
        assert socket.receive_json() == {
            "type": "protocol.error",
            "code": "invalid_message",
            "detail": "expected a presence.ping envelope with a UUID request_id",
        }
        socket.send_json({"type": "presence.ping", "request_id": request_id})
        pong = socket.receive_json()
        assert pong["type"] == "presence.pong"
        assert pong["request_id"] == request_id
        assert pong["organization_slug"] == "northstar"
        assert pong["subject"] == "local-developer"

    with pytest.raises(WebSocketDisconnect) as replay:
        with client.websocket_connect(
            f"/v1/realtime/ws?ticket={ticket}",
            headers={"origin": ALLOWED_ORIGIN},
        ):
            pass
    assert replay.value.code == 4401

    metrics = client.get("/metrics").text
    assert "atlas_websocket_messages_total" in metrics
    assert 'message_type="presence.ping"' in metrics


def test_rejected_origin_does_not_consume_ticket(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    ticket = issue_ticket(client, auth_headers)
    with pytest.raises(WebSocketDisconnect) as rejected:
        with client.websocket_connect(
            f"/v1/realtime/ws?ticket={ticket}",
            headers={"origin": "https://untrusted.example"},
        ):
            pass
    assert rejected.value.code == 4403

    # Origin checks precede ticket redemption, so the legitimate browser can still
    # use its ticket after an unrelated cross-site attempt.
    with client.websocket_connect(
        f"/v1/realtime/ws?ticket={ticket}",
        headers={"origin": ALLOWED_ORIGIN},
    ) as socket:
        request_id = str(uuid4())
        socket.send_json({"type": "presence.ping", "request_id": request_id})
        assert socket.receive_json()["request_id"] == request_id


def test_oversized_message_is_closed(client: TestClient, auth_headers: dict[str, str]) -> None:
    ticket = issue_ticket(client, auth_headers)
    with client.websocket_connect(
        f"/v1/realtime/ws?ticket={ticket}",
        headers={"origin": ALLOWED_ORIGIN},
    ) as socket:
        socket.send_text("x" * 2049)
        with pytest.raises(WebSocketDisconnect) as oversized:
            socket.receive_text()
    assert oversized.value.code == 4409
