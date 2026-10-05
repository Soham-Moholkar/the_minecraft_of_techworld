"""Repository AI security boundary, routing, persistence, and provider contracts."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import select

from atlas_api.ai_operations import AISLOTracker
from atlas_api.ai_routes import provider_dependency
from atlas_api.auth import Principal, require_principal
from atlas_api.config import Settings, get_settings
from atlas_api.database import get_session
from atlas_api.main import app
from atlas_api.models import AIUsageReservation, AuditEvent
from atlas_api.repository_ai import (
    AIProviderContractError,
    AIProviderUnavailable,
    ExplanationDraft,
    LineExplanation,
    LocalOpenAICompatibleProvider,
    OpenAIResponsesProvider,
    ProviderResult,
    ProviderStreamEvent,
    RepositoryExplainRequest,
    RepositoryPathError,
    RepositorySourceReader,
    RoutedCodeIntelligenceProvider,
    provider_health,
)


class FixedProvider:
    """Test double returns one explanation per trusted source line."""

    def explain(
        self,
        source: Any,
        request: RepositoryExplainRequest,
        *,
        tenant: str,
        subject: str,
    ) -> ProviderResult:
        assert tenant == "northstar" and subject
        return ProviderResult(
            draft=ExplanationDraft(
                overview="This bounded slice demonstrates the repository explanation contract.",
                architecture_relations=["The module belongs to the API service."],
                suggested_change=None,
                lines=[
                    LineExplanation(
                        line_number=number,
                        explanation="Explains the exact source line without changing it.",
                        keywords=[],
                        relations=[],
                    )
                    for number in source.code_by_line
                ],
            ),
            provider="openai",
            model="gpt-5.6-luna",
            input_tokens=100,
            output_tokens=50,
        )

    def stream_explain(
        self,
        source: Any,
        request: RepositoryExplainRequest,
        *,
        tenant: str,
        subject: str,
    ) -> Any:
        result = self.explain(source, request, tenant=tenant, subject=subject)
        yield ProviderStreamEvent(delta='{"overview":')
        yield ProviderStreamEvent(result=result)


def test_reader_rejects_traversal_secrets_binary_and_oversized_ranges(tmp_path: Path) -> None:
    (tmp_path / "apps").mkdir()
    (tmp_path / "apps" / "safe.py").write_text("value = 1\nprint(value)\n", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=private\n", encoding="utf-8")
    (tmp_path / "infra" / ".tools").mkdir(parents=True)
    (tmp_path / "infra" / "worker.py").write_text("units = 4\n", encoding="utf-8")
    (tmp_path / "infra" / ".tools" / "vendor.py").write_text("private = 1\n", encoding="utf-8")
    reader = RepositorySourceReader(tmp_path)
    source = reader.read(RepositoryExplainRequest(path="apps/safe.py", end_line=2))
    assert source.code_by_line == {1: "value = 1", 2: "print(value)"}
    assert [record.path for record in reader.catalog()] == ["apps/safe.py", "infra/worker.py"]
    assert reader.read(RepositoryExplainRequest(path="infra/worker.py")).code_by_line == {
        1: "units = 4"
    }
    for path in ("../.env", ".env", "apps/unknown.exe", "infra/.tools/vendor.py"):
        try:
            reader.read(RepositoryExplainRequest(path=path))
        except RepositoryPathError:
            pass
        else:
            raise AssertionError(f"unsafe path was accepted: {path}")
    for start, end in ((3, 2), (1, 121)):
        try:
            RepositoryExplainRequest(path="apps/safe.py", start_line=start, end_line=end)
        except ValueError:
            pass
        else:
            raise AssertionError("an invalid line range was accepted")
    (tmp_path / "apps" / "wide.py").write_text("x" * 8_001, encoding="utf-8")
    try:
        reader.read(RepositoryExplainRequest(path="apps/wide.py"))
    except RepositoryPathError as error:
        assert "8,000" in str(error)
    else:
        raise AssertionError("an oversized source line was accepted")


def test_api_lists_safe_files_and_reattaches_exact_source(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    app.dependency_overrides[provider_dependency] = lambda: FixedProvider()
    catalog = client.get("/v1/ai/repository/files", headers=auth_headers)
    assert catalog.status_code == 200
    assert any(item["path"] == "apps/api-python/src/atlas_api/config.py" for item in catalog.json())
    assert all(not item["path"].endswith(".env") for item in catalog.json())
    assert all("/dist/" not in item["path"] for item in catalog.json())
    providers = client.get("/v1/ai/repository/providers", headers=auth_headers)
    assert providers.status_code == 200
    assert [(item["provider"], item["detail"]) for item in providers.json()] == [
        ("openai", "unconfigured"),
        ("local", "disabled"),
    ]

    request = {
        "path": "apps/api-python/src/atlas_api/config.py",
        "start_line": 1,
        "end_line": 3,
        "intent": "explain",
    }
    response = client.post("/v1/ai/repository/explain", headers=auth_headers, json=request)
    assert response.status_code == 200, response.text
    body = response.json()
    expected = Path(request["path"]).read_text(encoding="utf-8").splitlines()[:3]
    assert [line["code"] for line in body["lines"]] == expected
    assert body["model"] == "gpt-5.6-luna"
    assert body["usage"] == {
        "input_tokens": 100,
        "output_tokens": 50,
        "estimated_cost_usd": 0.0,
    }
    session = next(app.dependency_overrides[get_session]())
    audit = session.scalar(select(AuditEvent).where(AuditEvent.action == "ai.repository.explained"))
    assert audit is not None and audit.details["path"] == request["path"]
    usage = session.scalar(select(AIUsageReservation))
    assert usage is not None and usage.status == "completed"
    assert usage.input_tokens == 100 and usage.output_tokens == 50


def test_api_normalizes_stream_and_audits_only_validated_result(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    app.dependency_overrides[provider_dependency] = lambda: FixedProvider()
    with client.stream(
        "POST",
        "/v1/ai/repository/explain/stream",
        headers=auth_headers,
        json={"path": "README.md", "start_line": 1, "end_line": 2},
    ) as response:
        body = response.read().decode()
    assert response.status_code == 200
    assert "event: delta" in body and "event: result" in body
    assert '"provider":"openai"' in body
    session = next(app.dependency_overrides[get_session]())
    audit = session.scalar(select(AuditEvent).where(AuditEvent.action == "ai.repository.streamed"))
    assert audit is not None and audit.details["path"] == "README.md"


def test_prompt_versions_are_immutable_tenant_scoped_and_reusable(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    first = client.post(
        "/v1/ai/repository/prompts",
        headers=auth_headers,
        json={
            "prompt_key": "line-explainer",
            "name": "Line explainer",
            "instruction": "Explain invariants and failure behavior for every selected line.",
        },
    )
    second = client.post(
        "/v1/ai/repository/prompts",
        headers=auth_headers,
        json={
            "prompt_key": "line-explainer",
            "name": "Line explainer with security",
            "instruction": "Explain invariants, security boundaries, and failures for each line.",
        },
    )
    assert first.status_code == 201 and second.status_code == 201
    assert [first.json()["version"], second.json()["version"]] == [1, 2]
    listed = client.get("/v1/ai/repository/prompts", headers=auth_headers).json()
    assert [item["version"] for item in listed] == [2, 1]

    class CapturingProvider(FixedProvider):
        instruction = ""

        def explain(
            self, source: Any, request: RepositoryExplainRequest, **kwargs: Any
        ) -> ProviderResult:
            self.instruction = request.instruction
            return super().explain(source, request, **kwargs)

    provider = CapturingProvider()
    app.dependency_overrides[provider_dependency] = lambda: provider
    response = client.post(
        "/v1/ai/repository/explain",
        headers=auth_headers,
        json={
            "path": "README.md",
            "start_line": 1,
            "end_line": 1,
            "instruction": "This inline value must be replaced.",
            "prompt_version_id": second.json()["id"],
        },
    )
    assert response.status_code == 200
    assert provider.instruction == second.json()["instruction"]
    assert response.json()["prompt_version_id"] == second.json()["id"]

    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="other-owner", organization_slug="other-tenant", roles=("owner",)
    )
    hidden = client.post(
        "/v1/ai/repository/explain",
        headers=auth_headers,
        json={
            "path": "README.md",
            "start_line": 1,
            "end_line": 1,
            "prompt_version_id": second.json()["id"],
        },
    )
    assert hidden.status_code == 404


def test_api_authorizes_and_validates_before_provider(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    provider = Mock(spec=FixedProvider)
    app.dependency_overrides[provider_dependency] = lambda: provider
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="viewer", organization_slug="northstar", roles=("viewer",)
    )
    denied = client.post(
        "/v1/ai/repository/explain",
        headers=auth_headers,
        json={"path": "README.md", "start_line": 1, "end_line": 2},
    )
    assert denied.status_code == 403
    provider.explain.assert_not_called()
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="owner", organization_slug="northstar", roles=("owner",)
    )
    unsafe = client.post(
        "/v1/ai/repository/explain",
        headers=auth_headers,
        json={"path": ".env", "start_line": 1, "end_line": 2},
    )
    assert unsafe.status_code == 404
    provider.explain.assert_not_called()


def test_api_redacts_provider_failures_and_unknown_tenant(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    body = {"path": "README.md", "start_line": 1, "end_line": 2}
    provider = Mock()
    app.dependency_overrides[provider_dependency] = lambda: provider
    provider.explain.side_effect = AIProviderContractError("private malformed output")
    invalid = client.post("/v1/ai/repository/explain", headers=auth_headers, json=body)
    assert invalid.status_code == 502 and "private" not in invalid.text
    provider.explain.side_effect = AIProviderUnavailable("provider unavailable")
    unavailable = client.post("/v1/ai/repository/explain", headers=auth_headers, json=body)
    assert unavailable.status_code == 503
    app.dependency_overrides[require_principal] = lambda: Principal(
        subject="owner", organization_slug="missing", roles=("owner",)
    )
    missing = client.post("/v1/ai/repository/explain", headers=auth_headers, json=body)
    assert missing.status_code == 404


def test_openai_adapter_uses_fixed_cost_router_and_structured_output() -> None:
    settings = Settings(
        openai_api_key=SecretStr("test-key-not-for-production"),
        repository_root=".",
    )
    source = RepositorySourceReader(Path(".")).read(
        RepositoryExplainRequest(path="README.md", start_line=1, end_line=2)
    )
    draft = ExplanationDraft(
        overview="The repository readme identifies ATLAS and its primary engineering purpose.",
        architecture_relations=[],
        suggested_change=None,
        lines=[
            LineExplanation(
                line_number=number,
                explanation="Document line.",
                keywords=[],
                relations=[],
            )
            for number in source.code_by_line
        ],
    )
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "output_text": draft.model_dump_json(),
        "usage": {"input_tokens": 200, "output_tokens": 100},
    }
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.post.return_value = response
    with patch("atlas_api.repository_ai.httpx.Client", return_value=client):
        result = OpenAIResponsesProvider(settings).explain(
            source,
            RepositoryExplainRequest(
                path="README.md", start_line=1, end_line=2, intent="change_plan"
            ),
            tenant="northstar",
            subject="owner",
        )
    assert result.model == "gpt-5.6-terra"
    assert result.provider == "openai"
    sent = client.post.call_args.kwargs["json"]
    assert sent["store"] is False
    assert sent["text"]["format"]["type"] == "json_schema"
    assert sent["reasoning"]["effort"] == "medium"
    assert "test-key" not in json.dumps(sent)
    assert OpenAIResponsesProvider(settings).estimate_cost("gpt-5.6-terra", 200, 100) > 0


def test_openai_adapter_requires_a_key_before_network_access() -> None:
    source = RepositorySourceReader(Path(".")).read(
        RepositoryExplainRequest(path="README.md", start_line=1, end_line=1)
    )
    with patch("atlas_api.repository_ai.httpx.Client") as client:
        provider = OpenAIResponsesProvider(Settings(openai_api_key=None))
        try:
            provider.explain(
                source,
                RepositoryExplainRequest(path="README.md", start_line=1, end_line=1),
                tenant="northstar",
                subject="owner",
            )
        except AIProviderUnavailable:
            pass
        else:
            raise AssertionError("missing key did not fail closed")
        client.assert_not_called()


def test_local_adapter_uses_configured_endpoint_without_identity_or_tools() -> None:
    settings = Settings(
        local_ai_enabled=True,
        local_ai_base_url="http://local-runtime.invalid/v1",
        local_ai_model="local-code-model",
        local_ai_api_key=SecretStr("local-runtime-key"),
    )
    source = RepositorySourceReader(Path(".")).read(
        RepositoryExplainRequest(path="README.md", start_line=1, end_line=2)
    )
    draft = ExplanationDraft(
        overview="The local provider explains this bounded readme source slice.",
        architecture_relations=[],
        suggested_change=None,
        lines=[
            LineExplanation(
                line_number=number,
                explanation="Document line.",
                keywords=[],
                relations=[],
            )
            for number in source.code_by_line
        ],
    )
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": draft.model_dump_json()}}],
        "usage": {"prompt_tokens": 40, "completion_tokens": 20},
    }
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.post.return_value = response
    with patch("atlas_api.repository_ai.httpx.Client", return_value=client):
        result = LocalOpenAICompatibleProvider(settings).explain(
            source,
            RepositoryExplainRequest(path="README.md", start_line=1, end_line=2, provider="local"),
            tenant="northstar",
            subject="owner@example.test",
        )
    assert result.provider == "local" and result.model == "local-code-model"
    call = client.post.call_args
    assert call.args[0] == "http://local-runtime.invalid/v1/chat/completions"
    sent = call.kwargs["json"]
    assert sent["response_format"]["type"] == "json_schema"
    assert "tools" not in sent
    assert "northstar" not in json.dumps(sent)
    assert "owner@example.test" not in json.dumps(sent)
    assert "local-runtime-key" not in json.dumps(sent)


def test_router_prefers_hosted_then_falls_back_to_enabled_local() -> None:
    source = RepositorySourceReader(Path(".")).read(
        RepositoryExplainRequest(path="README.md", start_line=1, end_line=1)
    )
    local_router = RoutedCodeIntelligenceProvider(Settings(local_ai_enabled=True))
    local_router.local.explain = Mock(
        return_value=FixedProvider().explain(
            source,
            RepositoryExplainRequest(path="README.md"),
            tenant="northstar",
            subject="owner",
        )
    )
    local_router.explain(
        source,
        RepositoryExplainRequest(path="README.md"),
        tenant="northstar",
        subject="owner",
    )
    local_router.local.explain.assert_called_once()

    hosted_router = RoutedCodeIntelligenceProvider(
        Settings(openai_api_key=SecretStr("test-key-not-for-production"), local_ai_enabled=True)
    )
    hosted_router.openai.explain = Mock(
        return_value=FixedProvider().explain(
            source,
            RepositoryExplainRequest(path="README.md"),
            tenant="northstar",
            subject="owner",
        )
    )
    hosted_router.explain(
        source,
        RepositoryExplainRequest(path="README.md"),
        tenant="northstar",
        subject="owner",
    )
    hosted_router.openai.explain.assert_called_once()


def test_auto_router_falls_back_only_when_hosted_is_unavailable() -> None:
    source = RepositorySourceReader(Path(".")).read(
        RepositoryExplainRequest(path="README.md", start_line=1, end_line=1)
    )
    request = RepositoryExplainRequest(path="README.md")
    router = RoutedCodeIntelligenceProvider(
        Settings(
            openai_api_key=SecretStr("test-key-not-for-production"),
            local_ai_enabled=True,
        )
    )
    router.openai.explain = Mock(side_effect=AIProviderUnavailable("hosted down"))
    router.local.explain = Mock(
        return_value=FixedProvider().explain(source, request, tenant="northstar", subject="owner")
    )
    result = router.explain(source, request, tenant="northstar", subject="owner")
    assert result.provider == "openai"  # FixedProvider's neutral test result.
    assert result.fallback_from == "openai"
    router.local.explain.assert_called_once()

    router.local.explain.reset_mock()
    try:
        router.explain(
            source,
            request.model_copy(update={"provider": "openai"}),
            tenant="northstar",
            subject="owner",
        )
    except AIProviderUnavailable:
        pass
    else:
        raise AssertionError("explicit hosted selection unexpectedly fell back")
    router.local.explain.assert_not_called()


def test_stream_router_falls_back_only_before_the_first_delta() -> None:
    source = RepositorySourceReader(Path(".")).read(
        RepositoryExplainRequest(path="README.md", start_line=1, end_line=1)
    )
    request = RepositoryExplainRequest(path="README.md")
    router = RoutedCodeIntelligenceProvider(
        Settings(
            openai_api_key=SecretStr("test-key-not-for-production"),
            local_ai_enabled=True,
        )
    )

    def unavailable_stream(*args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        raise AIProviderUnavailable("hosted down before streaming")
        yield  # pragma: no cover - preserves the generator contract

    router.openai.stream_explain = unavailable_stream  # type: ignore[method-assign]
    router.local.stream_explain = FixedProvider().stream_explain  # type: ignore[method-assign]
    events = list(router.stream_explain(source, request, tenant="northstar", subject="owner"))
    assert events[-1].result is not None
    assert events[-1].result.fallback_from == "openai"


def test_budget_reservation_denies_before_provider_call(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    settings = Settings(
        repository_root=".",
        openai_api_key=SecretStr("test-key-not-for-production"),
        ai_monthly_budget_usd=0.1,
        ai_run_reservation_usd=0.2,
    )
    app.dependency_overrides[get_settings] = lambda: settings
    provider = Mock(spec=FixedProvider)
    app.dependency_overrides[provider_dependency] = lambda: provider
    denied = client.post(
        "/v1/ai/repository/explain",
        headers=auth_headers,
        json={"path": "README.md", "start_line": 1, "end_line": 1},
    )
    assert denied.status_code == 429
    provider.explain.assert_not_called()
    operations = client.get("/v1/ai/repository/operations", headers=auth_headers)
    assert operations.status_code == 200
    assert operations.json()["budget"] == {
        "monthly_limit_usd": 0.1,
        "committed_usd": 0.0,
        "reserved_usd": 0.0,
        "remaining_usd": 0.1,
    }


def test_slo_tracker_calculates_bounded_availability_and_p95() -> None:
    tracker = AISLOTracker()
    tracker.record("success", 0.1)
    tracker.record("success", 0.2)
    tracker.record("failure", 0.5)
    snapshot = tracker.snapshot(
        Settings(ai_slo_availability_target=0.6, ai_slo_p95_seconds_target=0.5)
    )
    assert snapshot.sample_count == 3
    assert snapshot.availability == 0.666667
    assert snapshot.p95_seconds == 0.5
    assert snapshot.availability_met is True and snapshot.latency_met is True


def test_provider_health_is_redacted_and_bounded() -> None:
    settings = Settings(
        openai_api_key=None,
        local_ai_enabled=True,
        local_ai_base_url="http://local-runtime.invalid/v1",
        local_ai_model="local-code-model",
    )
    response = Mock()
    response.raise_for_status.return_value = None
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.get.return_value = response
    with patch("atlas_api.repository_ai.httpx.Client", return_value=client) as constructor:
        statuses = provider_health(settings)
    assert statuses[0].detail == "unconfigured"
    assert statuses[1].detail == "ready" and statuses[1].reachable is True
    assert "local-runtime.invalid" not in json.dumps([item.model_dump() for item in statuses])
    assert constructor.call_args.kwargs["timeout"] == 2


def _streaming_client(lines: list[str]) -> tuple[Mock, Mock]:
    response = Mock()
    response.raise_for_status.return_value = None
    response.iter_lines.return_value = iter(lines)
    stream_context = Mock()
    stream_context.__enter__ = Mock(return_value=response)
    stream_context.__exit__ = Mock(return_value=False)
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.stream.return_value = stream_context
    return client, response


def test_hosted_and_local_streams_share_one_validated_event_contract() -> None:
    source = RepositorySourceReader(Path(".")).read(
        RepositoryExplainRequest(path="README.md", start_line=1, end_line=1)
    )
    draft = ExplanationDraft(
        overview="The streamed explanation covers the selected repository line.",
        architecture_relations=[],
        suggested_change=None,
        lines=[
            LineExplanation(
                line_number=1,
                explanation="Document line.",
                keywords=[],
                relations=[],
            )
        ],
    ).model_dump_json()
    first, second = draft[: len(draft) // 2], draft[len(draft) // 2 :]

    hosted_lines = [
        f"data: {json.dumps({'type': 'response.output_text.delta', 'delta': first})}",
        f"data: {json.dumps({'type': 'response.output_text.delta', 'delta': second})}",
        "data: "
        + json.dumps(
            {
                "type": "response.completed",
                "response": {"usage": {"input_tokens": 30, "output_tokens": 15}},
            }
        ),
        "data: [DONE]",
    ]
    hosted_client, _ = _streaming_client(hosted_lines)
    hosted = OpenAIResponsesProvider(
        Settings(openai_api_key=SecretStr("test-key-not-for-production"))
    )
    with patch("atlas_api.repository_ai.httpx.Client", return_value=hosted_client):
        hosted_events = list(
            hosted.stream_explain(
                source,
                RepositoryExplainRequest(path="README.md", end_line=1),
                tenant="northstar",
                subject="owner",
            )
        )
    assert "".join(event.delta or "" for event in hosted_events) == draft
    assert hosted_events[-1].result is not None
    assert hosted_events[-1].result.provider == "openai"
    assert hosted_events[-1].result.input_tokens == 30

    local_lines = [
        f"data: {json.dumps({'choices': [{'delta': {'content': first}}]})}",
        f"data: {json.dumps({'choices': [{'delta': {'content': second}}]})}",
        'data: {"choices":[],"usage":{"prompt_tokens":25,"completion_tokens":12}}',
        "data: [DONE]",
    ]
    local_client, _ = _streaming_client(local_lines)
    local = LocalOpenAICompatibleProvider(
        Settings(local_ai_enabled=True, local_ai_model="local-code-model")
    )
    with patch("atlas_api.repository_ai.httpx.Client", return_value=local_client):
        local_events = list(
            local.stream_explain(
                source,
                RepositoryExplainRequest(path="README.md", end_line=1, provider="local"),
                tenant="northstar",
                subject="owner",
            )
        )
    assert "".join(event.delta or "" for event in local_events) == draft
    assert local_events[-1].result is not None
    assert local_events[-1].result.provider == "local"
    assert local_events[-1].result.output_tokens == 12
